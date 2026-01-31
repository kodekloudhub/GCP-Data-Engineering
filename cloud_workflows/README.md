# GCP Cloud Workflows - BigQuery Public Dataset Transformation

This folder contains two production-ready Cloud Workflows YAML files for transforming NYC taxi public data in BigQuery. Both workflows use the `kodekloud-gcp-training` project and are designed for manual triggering via the Cloud Workflows UI.

## Overview

### Workflow 1: Linear Pipeline (`linear_workflow.yaml`)
Sequential execution of all transformation steps:
```
Initialize → Create Fact Table → Populate Fact Table → Create Summary → Populate Summary → Complete
```

**Use Case**: Simple, dependency-driven workflow where each step must complete before the next begins.

### Workflow 2: Branching Pipeline (`branching_workflow.yaml`)
Parallel execution with data split by trip distance, then convergence to aggregation:
```
Initialize → Create Fact Table → (Branch 1: Long Trips in Parallel | Branch 2: Short Trips) → Converge → Create Summary → Populate Summary → Complete
```

**Use Case**: Demonstrating parallel processing - splits NYC taxi data into two distance categories, processes both simultaneously, then aggregates results.

## Key Features

✅ **No Table Deletion**: Both workflows preserve final tables for analysis
✅ **Manual Triggering**: No schedules - execute on-demand from UI
✅ **Basic Error Handling**: Try-catch blocks on BigQuery jobs with retry logic (2 retries, exponential backoff)
✅ **Comprehensive Logging**: INFO and ERROR level logs for monitoring
✅ **Hardcoded Project**: Uses `kodekloud-gcp-training` project
✅ **Public Dataset**: Queries NYC taxi data from `bigquery-public-data.new_york_taxi.tlc_green_trips` with borough lookup via `taxi_zone_lookup`

## Public Dataset (BigQuery)

The workflows use the **updated** NYC taxi public dataset:

| Resource | Name | Description |
|----------|------|-------------|
| Trip data | `bigquery-public-data.new_york_taxi.tlc_green_trips` | Green taxi trips (partitioned by date; use `lpep_pickup_datetime`, `lpep_dropoff_datetime`, `PULocationID`, `DOLocationID`) |
| Zone lookup | `bigquery-public-data.new_york_taxi.taxi_zone_lookup` | Maps `LocationID` to `Borough` and `Zone` for pickup/dropoff borough |

The filter date is set to `2019-01-15` so the workflow returns data. You can change it to any date present in `tlc_green_trips`.

## Prerequisites

1. **GCP Project**: `kodekloud-gcp-training`
2. **Cloud Workflows API**: Already enabled
3. **BigQuery API**: Already enabled
4. **IAM Permissions**: Service account has:
   - `roles/bigquery.dataEditor` (create/edit tables)
   - `roles/bigquery.jobUser` (submit BigQuery jobs)
   - `roles/workflows.invoker` (execute workflows)
5. **BigQuery Dataset — create first**: The workflows do **not** create the dataset. You must create the `cloudworkflows_demo` dataset **before** running either pipeline:
   ```bash
   bq mk --dataset --location=US kodekloud-gcp-training:cloudworkflows_demo
   ```
   If the dataset already exists, this command is safe to run (it will report that the dataset exists). Run it once per project before the first workflow execution.

## Workflow Details

### Linear Workflow Step-by-Step

1. **init_variables**: Set project, dataset, and table names
2. **log_workflow_start**: Log workflow initiation
3. **create_fact_table**: Create empty fact table with schema
   - Columns: trip_id, pickup_datetime, passenger_count, fare_amount, etc.
4. **populate_fact_table**: Insert data from public dataset
   - Source: `tlc_green_trips` joined with `taxi_zone_lookup` for pickup/dropoff borough
   - Filters: trip_distance > 0, fare_amount > 0, passenger_count > 0, date = 2019-01-15
   - Limits: 10,000 records for demo
   - Calculates: trip_duration_minutes using TIMESTAMP_DIFF
5. **create_summary_table**: Create aggregate table schema
6. **populate_summary_table**: Aggregate by pickup_borough
   - Metrics: total_trips, avg_fare_per_trip, avg_trip_duration_minutes
7. **log_workflow_completion**: Log successful completion

### Branching Workflow Step-by-Step

1. **init_variables**: Set project and table names
2. **log_workflow_start**: Log workflow with branching strategy
3. **create_fact_table**: Create fact table with `distance_category` field
4. **parallel_branches**: Execute 2 branches simultaneously
   
   **Branch 1 - Long Trips**:
   - Query trips where `trip_distance > 5`
   - Add `distance_category = 'LONG'`
   - Insert up to 5,000 records
   - Error handling with retry logic
   
   **Branch 2 - Short Trips**:
   - Query trips where `trip_distance <= 5`
   - Add `distance_category = 'SHORT'`
   - Insert up to 5,000 records
   - Error handling with retry logic

5. **log_branches_converge**: Log convergence point
6. **create_summary_table**: Create aggregate table with distance_category
7. **populate_summary_table**: GROUP BY borough AND distance_category
   - Compares metrics between long and short trips
8. **log_workflow_completion**: Log successful completion

## Output Tables

### Linear Workflow
- **fact_taxi_trips_linear**: Denormalized trip records (~10K rows)
- **agg_taxi_summary_linear**: Aggregated metrics by borough

### Branching Workflow
- **fact_taxi_trips_branched**: Trip records split by distance category (~10K rows)
- **agg_taxi_summary_branched**: Aggregated metrics by borough and distance

## Query Examples

### View Linear Fact Table
```sql
SELECT 
  trip_id, 
  pickup_datetime, 
  fare_amount,
  trip_duration_minutes
FROM `kodekloud-gcp-training.cloudworkflows_demo.fact_taxi_trips_linear`
LIMIT 10;
```

### View Linear Summary
```sql
SELECT 
  pickup_borough,
  total_trips,
  avg_fare_per_trip,
  avg_trip_duration_minutes
FROM `kodekloud-gcp-training.cloudworkflows_demo.agg_taxi_summary_linear`
ORDER BY total_trips DESC;
```

### View Branched Summary (Compare Long vs Short Trips)
```sql
SELECT 
  pickup_borough,
  distance_category,
  total_trips,
  avg_fare_per_trip,
  avg_trip_duration_minutes
FROM `kodekloud-gcp-training.cloudworkflows_demo.agg_taxi_summary_branched`
ORDER BY distance_category, total_trips DESC;
```

## Table Persistence

**Important**: Both workflows **DO NOT DELETE** the created BigQuery tables. After execution:
- Fact tables remain in `cloudworkflows_demo` dataset
- Aggregate summary tables remain in `cloudworkflows_demo` dataset
- Tables can be queried and analyzed anytime
- Manual cleanup can be done later via BigQuery UI or CLI if needed

## Cleanup

To delete the demo tables and dataset after testing:

```bash
# Delete individual tables
bq rm -f kodekloud-gcp-training:cloudworkflows_demo.fact_taxi_trips_linear
bq rm -f kodekloud-gcp-training:cloudworkflows_demo.agg_taxi_summary_linear
bq rm -f kodekloud-gcp-training:cloudworkflows_demo.fact_taxi_trips_branched
bq rm -f kodekloud-gcp-training:cloudworkflows_demo.agg_taxi_summary_branched

# OR delete the entire dataset (all tables inside)
bq rm -r -d kodekloud-gcp-training:cloudworkflows_demo
```

## Customization

### Change Date Filter
Update the date in both workflows (currently `2019-01-15`). Use a date that exists in the public dataset; `tlc_green_trips` is partitioned and contains historical data:
```yaml
WHERE DATE(t.lpep_pickup_datetime) = CAST('2019-01-15' AS DATE)
```

### Adjust Record Limits
Modify `LIMIT` clause in populate queries:
```yaml
LIMIT 10000  # Change to desired number
```

### Add Additional Branches
Extend the `parallel_branches` section with more distance ranges:
```yaml
parallel:
  branches:
    - branch_long_distance: ...
    - branch_medium_distance: ...  # NEW
    - branch_short_distance: ...
```

### Change Dataset Location
Update `dataset_location` and BigQuery region:
```yaml
dataset_location: "EU"  # or another location
```

## Next Steps

1. **Monitor Executions**: Check logs in Cloud Workflows UI after each run
2. **Verify Data**: Query BigQuery tables to validate transformation results
3. **Compare Results**: Run both workflows and compare linear vs. branched output
4. **Extend Pipeline**: Add more branches or aggregation steps
5. **Set Triggers**: Connect workflows to Cloud Pub/Sub, Cloud Scheduler, or Cloud Events

## References

- [Cloud Workflows Documentation](https://cloud.google.com/workflows/docs)
- [Workflows YAML Syntax](https://cloud.google.com/workflows/docs/reference/syntax)
- [BigQuery REST API](https://cloud.google.com/bigquery/docs/reference/rest/v2)
- [NYC Taxi Public Dataset](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=new_york_taxi) — uses `tlc_green_trips` (partitioned) and `taxi_zone_lookup` for borough names
