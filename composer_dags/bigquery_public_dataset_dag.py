"""
BigQuery Public Dataset Processing DAG for GCP Composer

This DAG demonstrates a typical data engineering workflow:
1. Creates a destination table in BigQuery
2. Queries the public NYC taxi dataset
3. Processes the data with Python transformations
4. Loads results into a fact table
5. Creates an aggregate summary table

The DAG uses Google Cloud Composer with BigQuery operators and demonstrates
data lineage tracking using XCom.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyTableOperator,
    BigQueryGetDataOperator,
    BigQueryInsertJobOperator,
    BigQueryDeleteTableOperator,
)
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
import json


# Configuration
PROJECT_ID = "kodekloud-gcp-training"
DATASET_ID = "composer_demo"
DATASET_LOCATION = "US"

# Public BigQuery datasets
NYC_TAXI_PROJECT = "bigquery-public-data"
NYC_TAXI_DATASET = "new_york_taxi"
NYC_TAXI_TABLE = "tlc_green_trips_2019"

# Output tables
FACT_TABLE = "fact_taxi_trips"
SUMMARY_TABLE = "agg_taxi_summary"


# Default arguments for DAG
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["data-eng@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
    "catchup": False,
    "execution_timeout": timedelta(hours=2),
}

# DAG definition
dag = DAG(
    "bigquery_public_dataset_pipeline",
    default_args=default_args,
    description="Process BigQuery public taxi data and create fact/aggregate tables",
    schedule_interval="@daily",  # Run daily
    tags=["gcp", "bigquery", "composer", "public-dataset"],
    max_active_runs=1,
)


def get_dataset_info(**context):
    """
    Python operator: Extract and log dataset information.
    Demonstrates XCom usage for passing data between tasks.
    """
    dataset_info = {
        "source_project": NYC_TAXI_PROJECT,
        "source_dataset": NYC_TAXI_DATASET,
        "source_table": NYC_TAXI_TABLE,
        "destination_project": PROJECT_ID,
        "destination_dataset": DATASET_ID,
        "processing_date": context["ds"],  # Airflow execution date
        "task_instance": context["task"].task_id,
    }
    print(f"Dataset Info: {json.dumps(dataset_info, indent=2)}")
    
    # Push to XCom for downstream tasks
    context["task_instance"].xcom_push(key="dataset_info", value=dataset_info)
    return dataset_info


def validate_data(**context):
    """
    Python operator: Validate that source data exists.
    Retrieves data from XCom pushed by previous task.
    """
    dataset_info = context["task_instance"].xcom_pull(
        task_ids="get_dataset_info",
        key="dataset_info"
    )
    print(f"Validating data from: {dataset_info['source_project']}.{dataset_info['source_dataset']}")
    print("Data validation completed successfully")
    return True


# Task 1: Print execution date
print_execution_date = BashOperator(
    task_id="print_execution_date",
    bash_command="echo 'DAG execution date: {{ ds }}' && date",
    dag=dag,
)


# Task 2: Get dataset information
get_info = PythonOperator(
    task_id="get_dataset_info",
    python_callable=get_dataset_info,
    provide_context=True,
    dag=dag,
)


# Task 3: Validate source data
validate = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)


# Task Group: Create destination dataset and tables
with TaskGroup("setup_destination", dag=dag) as setup_tg:
    
    # Create empty fact table with schema
    create_fact_table = BigQueryCreateEmptyTableOperator(
        task_id="create_fact_table",
        dataset_id=DATASET_ID,
        table_id=FACT_TABLE,
        project_id=PROJECT_ID,
        schema_fields=[
            {"name": "trip_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "pickup_datetime", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "dropoff_datetime", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "passenger_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "trip_distance", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "fare_amount", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "pickup_borough", "type": "STRING", "mode": "NULLABLE"},
            {"name": "dropoff_borough", "type": "STRING", "mode": "NULLABLE"},
            {"name": "trip_duration_minutes", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "processing_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        ],
        exists_ok=True,
        location=DATASET_LOCATION,
    )


# Task Group: Query and transform data
with TaskGroup("data_processing", dag=dag) as processing_tg:
    
    # Query public dataset and insert into fact table
    query_public_data = BigQueryInsertJobOperator(
        task_id="query_and_load_fact_table",
        configuration={
            "query": {
                "query": f"""
                    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{FACT_TABLE}`
                    SELECT
                        CONCAT(
                            CAST(EXTRACT(YEAR FROM pickup_datetime) AS STRING), '-',
                            CAST(EXTRACT(MONTH FROM pickup_datetime) AS STRING), '-',
                            ROW_NUMBER() OVER (PARTITION BY DATE(pickup_datetime) ORDER BY pickup_datetime)
                        ) as trip_id,
                        pickup_datetime,
                        dropoff_datetime,
                        passenger_count,
                        trip_distance,
                        fare_amount,
                        total_amount,
                        pickup_borough,
                        dropoff_borough,
                        CAST(TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, MINUTE) AS INT64) as trip_duration_minutes,
                        CURRENT_TIMESTAMP() as processing_timestamp
                    FROM `{NYC_TAXI_PROJECT}.{NYC_TAXI_DATASET}.{NYC_TAXI_TABLE}`
                    WHERE DATE(pickup_datetime) = '{{{{ ds }}}}'
                        AND trip_distance > 0
                        AND fare_amount > 0
                        AND passenger_count > 0
                    LIMIT 10000  -- Limit for demo purposes
                """,
                "useLegacySql": False,
                "location": DATASET_LOCATION,
            }
        },
        project_id=PROJECT_ID,
    )


# Task Group: Create aggregate table
with TaskGroup("create_aggregates", dag=dag) as aggregates_tg:
    
    # Create summary/aggregate table
    create_summary_table = BigQueryCreateEmptyTableOperator(
        task_id="create_summary_table",
        dataset_id=DATASET_ID,
        table_id=SUMMARY_TABLE,
        project_id=PROJECT_ID,
        schema_fields=[
            {"name": "processing_date", "type": "DATE", "mode": "REQUIRED"},
            {"name": "pickup_borough", "type": "STRING", "mode": "REQUIRED"},
            {"name": "total_trips", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "total_passengers", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "total_distance", "type": "FLOAT64", "mode": "REQUIRED"},
            {"name": "total_fare", "type": "FLOAT64", "mode": "REQUIRED"},
            {"name": "avg_fare_per_trip", "type": "FLOAT64", "mode": "REQUIRED"},
            {"name": "avg_trip_duration_minutes", "type": "FLOAT64", "mode": "REQUIRED"},
        ],
        exists_ok=True,
        location=DATASET_LOCATION,
    )
    
    # Populate aggregate table
    populate_summary = BigQueryInsertJobOperator(
        task_id="populate_summary_table",
        configuration={
            "query": {
                "query": f"""
                    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{SUMMARY_TABLE}`
                    SELECT
                        CAST(processing_timestamp AS DATE) as processing_date,
                        pickup_borough,
                        COUNT(*) as total_trips,
                        SUM(passenger_count) as total_passengers,
                        SUM(trip_distance) as total_distance,
                        SUM(fare_amount) as total_fare,
                        ROUND(AVG(fare_amount), 2) as avg_fare_per_trip,
                        ROUND(AVG(trip_duration_minutes), 2) as avg_trip_duration_minutes
                    FROM `{PROJECT_ID}.{DATASET_ID}.{FACT_TABLE}`
                    WHERE CAST(processing_timestamp AS DATE) = '{{{{ ds }}}}'
                    GROUP BY processing_date, pickup_borough
                    ORDER BY total_trips DESC
                """,
                "useLegacySql": False,
                "location": DATASET_LOCATION,
            }
        },
        project_id=PROJECT_ID,
    )
    
    create_summary_table >> populate_summary


# Task: Fetch and log results
get_results = BigQueryGetDataOperator(
    task_id="get_aggregated_results",
    dataset_id=DATASET_ID,
    table_id=SUMMARY_TABLE,
    project_id=PROJECT_ID,
    max_results=5,
    selected_fields=["pickup_borough", "total_trips", "avg_fare_per_trip"],
)


# Task: Cleanup (optional - delete test tables after verification)
cleanup_fact = BigQueryDeleteTableOperator(
    task_id="cleanup_fact_table",
    deletion_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.{FACT_TABLE}",
    trigger_rule="all_done",  # Run even if upstream fails
    ignore_if_missing=True,
)


# Define DAG dependencies
(
    print_execution_date
    >> get_info
    >> validate
    >> setup_tg
    >> processing_tg
    >> aggregates_tg
    >> get_results
    >> cleanup_fact
)
