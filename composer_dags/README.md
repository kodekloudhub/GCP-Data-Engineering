# GCP Cloud Composer DAG - BigQuery Public Dataset Pipeline

A production-ready Apache Airflow DAG for Google Cloud Composer that demonstrates ETL patterns using BigQuery public datasets.

## Overview

This DAG (`bigquery_public_dataset_dag.py`) processes public NYC taxi data from BigQuery and creates fact and aggregate tables. It showcases:

- **BigQuery Operators**: Creating tables, running queries, fetching results
- **Task Groups**: Organizing complex workflows
- **XCom**: Passing data between tasks
- **Error Handling**: Retries and failure notifications
- **Data Pipeline**: From source → transformation → aggregation

### DAG Architecture

```
print_execution_date
    ↓
get_dataset_info (XCom Push)
    ↓
validate_data (XCom Pull)
    ↓
┌─ setup_destination ─┐
│  create_fact_table  │
└─────────────────────┘
    ↓
┌─ data_processing ─────────────────────┐
│  query_and_load_fact_table            │
│  (NYC taxi data → fact_taxi_trips)    │
└───────────────────────────────────────┘
    ↓
┌─ create_aggregates ─────────────────────┐
│  create_summary_table                   │
│  populate_summary_table (GROUP BY)      │
└─────────────────────────────────────────┘
    ↓
get_aggregated_results
    ↓
cleanup_fact_table
```

## Prerequisites

### Verify Composer Environment Status
```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
export COMPOSER_ENV="composer-demo"  # Replace with your environment name
export COMPOSER_REGION="us-central1" # Replace with your region

# Verify Composer is running
gcloud composer environments describe $COMPOSER_ENV --location $COMPOSER_REGION

# Check Airflow Web UI is accessible
gcloud composer environments describe $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --format='value(config.airflowUri)'
```

### Verify IAM Permissions
Your Composer service account needs these roles (typically assigned by default):
- `roles/bigquery.dataEditor` (create/edit BigQuery tables)
- `roles/bigquery.jobUser` (submit BigQuery jobs)

```bash
# Get Composer service account
SA=$(gcloud composer environments describe $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --format='value(config.nodeConfig.serviceAccount)')

# Verify roles
gcloud projects get-iam-policy $GCP_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA}"
```

## Deployment

Your DAG is ready to deploy to the running Composer environment. Choose your preferred method:

### Method 1: Upload via gcloud CLI (Recommended)
```bash
gcloud composer environments storage dags import \
    --environment $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --source bigquery_public_dataset_dag.py
```

### Method 2: Upload via GCS (Direct)
```bash
# Find Composer bucket
BUCKET=$(gcloud composer environments describe $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --format='value(config.dagGcsPrefix)' | sed 's|gs://||' | cut -d'/' -f1)

# Copy DAG file
gsutil cp bigquery_public_dataset_dag.py gs://${BUCKET}/dags/
```

### Method 3: Manual Web UI
1. Get the Airflow Web UI URL:
   ```bash
   gcloud composer environments describe $COMPOSER_ENV \
       --location $COMPOSER_REGION \
       --format='value(config.airflowUri)'
   ```
2. Click **DAGs** tab → **Upload a file**
3. Select `bigquery_public_dataset_dag.py`

The DAG is ready to use with no additional configuration needed!

### Key Configuration Values (in DAG code)
```python
PROJECT_ID = "kodekloud-gcp-training"  # Hardcoded project ID
DATASET_ID = "composer_demo"            # Output dataset
NYC_TAXI_PROJECT = "bigquery-public-data"
NYC_TAXI_DATASET = "new_york_taxi"
NYC_TAXI_TABLE = "tlc_green_trips_2019"
```

The DAG is pre-configured to use the `kodekloud-gcp-training` project. No additional variable setup is required.

## DAG Details

### Tasks Breakdown

1. **print_execution_date** (BashOperator)
   - Logs the DAG execution date and current time

2. **get_dataset_info** (PythonOperator)
   - Extracts source/destination metadata
   - Pushes data via XCom for downstream tasks

3. **validate_data** (PythonOperator)
   - Validates source data availability
   - Retrieves metadata from XCom

4. **setup_destination** (TaskGroup)
   - **create_fact_table**: Creates BigQuery table with schema
   - Defines fields: trip_id, pickup_datetime, fare_amount, trip_duration_minutes, etc.

5. **data_processing** (TaskGroup)
   - **query_and_load_fact_table**: Queries public NYC taxi data
   - Filters: trip_distance > 0, fare_amount > 0, passenger_count > 0
   - Calculates: trip_duration_minutes using TIMESTAMP_DIFF
   - Limits to 10,000 records per day (demo purposes)

6. **create_aggregates** (TaskGroup)
   - **create_summary_table**: Creates aggregate table schema
   - **populate_summary_table**: Runs GROUP BY query
   - Aggregates: total_trips, total_passengers, avg_fare_per_trip by borough

7. **get_aggregated_results** (BigQueryGetDataOperator)
   - Fetches top 5 results from summary table
   - Logs results to DAG execution logs

8. **cleanup_fact_table** (BigQueryDeleteTableOperator)
   - Removes fact table (optional - set `trigger_rule="all_done"`)
   - Change `trigger_rule` to `"success"` to keep tables for inspection

### Query Logic

**Fact Table Query**: Transforms raw taxi trips
```sql
SELECT trip_id, pickup_datetime, fare_amount, 
       TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, MINUTE) as trip_duration_minutes
FROM `bigquery-public-data.new_york_taxi.tlc_green_trips_2019`
WHERE trip_distance > 0 AND fare_amount > 0
```

**Aggregate Query**: Summarizes by borough
```sql
SELECT pickup_borough, COUNT(*) as total_trips, 
       AVG(fare_amount) as avg_fare_per_trip
FROM fact_taxi_trips
GROUP BY pickup_borough
```

## Monitoring & Debugging

### View DAG in Web UI
```bash
# Open Airflow Web UI
gcloud composer environments describe $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --format='value(config.airflowUri)'
```

Open the URL in your browser and navigate to **DAGs** → `bigquery_public_dataset_pipeline`

### Monitor Task Execution
1. Open Airflow Web UI
2. Click **DAGs** → `bigquery_public_dataset_pipeline`
3. View **Tree View** or **Gantt Chart**
4. Click task to see logs

### Check Logs via CLI
```bash
# Stream logs for a specific task
gcloud composer environments storage logs list \
    --environment composer-demo \
    --location us-central1
```

### Manual DAG Trigger
```bash
# Trigger DAG for a specific date
gcloud composer environments run $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    dags test -- bigquery_public_dataset_pipeline 2024-01-15
```

## Troubleshooting

### Issue: "Dataset not found" error
**Solution**: Verify the `kodekloud-gcp-training` project has the `composer_demo` dataset. Create it if needed:
```bash
bq mk --dataset --location=US kodekloud-gcp-training:composer_demo
```

### Issue: Permission Denied
**Solution**: Verify BigQuery roles for Composer service account
```bash
SA=$(gcloud composer environments describe $COMPOSER_ENV \
    --location $COMPOSER_REGION \
    --format='value(config.nodeConfig.serviceAccount)')

# Grant BigQuery admin role if needed
gcloud projects add-iam-policy-binding kodekloud-gcp-training \
    --member=serviceAccount:$SA \
    --role=roles/bigquery.admin
```

### Issue: "Public dataset not accessible"
**Solution**: Public datasets don't require additional setup. Verify BigQuery API is enabled:
```bash
gcloud services list --enabled | grep bigquery
```

### Issue: DAG not appearing
**Solution**: Wait 5-10 minutes for DAG sync, or check the Airflow scheduler logs:
```bash
gcloud composer environments logs list --environment $COMPOSER_ENV --location $COMPOSER_REGION
```

## Customization

### Change Schedule Frequency
```python
# In DAG definition
schedule_interval="@daily"      # Daily (default)
schedule_interval="@hourly"     # Every hour
schedule_interval="0 2 * * *"   # 2 AM UTC (cron format)
schedule_interval=None          # Manual trigger only
```

### Adjust Data Limits
```python
# In query_and_load_fact_table query
LIMIT 10000  # Change to your desired record count
```

### Add Email Alerts
```python
default_args = {
    "email": ["your-email@example.com"],
    "email_on_failure": True,
    "email_on_retry": True,
}
```

### Keep Tables After DAG Completes
```python
# Modify cleanup_fact_table task
cleanup_fact = BigQueryDeleteTableOperator(
    task_id="cleanup_fact_table",
    ...
    trigger_rule="success",  # Only delete on success
    # Or set to skip deletion:
    # trigger_rule="skipped",
)
```

## Best Practices Applied

✅ **Idempotent Operations**: Tables created with `exists_ok=True`
✅ **Error Handling**: Retries configured with exponential backoff
✅ **Data Validation**: Python operator validates source before processing
✅ **Task Organization**: TaskGroups organize logical workflow steps
✅ **Data Lineage**: XCom passes metadata through pipeline
✅ **Cleanup**: Trigger rules ensure cleanup runs after completion
✅ **Templating**: Uses `{{ ds }}` for dynamic date handling
✅ **Configuration**: External variables instead of hardcoded values

## Next Steps

1. **Extend Pipeline**: Add more transformations, ML predictions, or notifications
2. **Schedule Production**: Set `schedule_interval` and adjust `start_date`
3. **Add Tests**: Use `@task.branch` for conditional logic
4. **Monitor Costs**: Query BigQuery slot usage and set budget alerts
5. **Parameterize**: Use Airflow Params for runtime customization

## References

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Google Cloud Composer Docs](https://cloud.google.com/composer/docs)
- [Airflow BigQuery Provider](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/bigquery.html)
- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [NYC Taxi Dataset](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=new_york_taxi)

