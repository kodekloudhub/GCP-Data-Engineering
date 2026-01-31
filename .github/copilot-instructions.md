# GCP Data Engineering Copilot Instructions

## Project Overview
This is a **GCP data engineering training repository** demonstrating data ingestion, transformation, and containerized job execution patterns. The codebase contains two main workflows:

1. **BigQuery Data Generation**: Python scripts that generate and upload test datasets (gaming transactions, in-flight purchases)
2. **Cloud Run Jobs Pipeline**: Containerized ETL job that reads raw data from BigQuery, transforms it into fact and aggregate tables

## Architecture & Data Flow

### BigQuery Workflow
```
Python Data Generator → CSV File → BigQuery Dataset/Table
```
- **Location**: `BigQuery/BigQuery_Upload/` and `BigQuery/BigQuery_GCS_Upload/`
- **Pattern**: Data generation scripts (with and without dependencies) → CSV output → manual upload to BigQuery
- **Key Design**: Provides both "simple" (no deps) and full-featured versions for flexibility
- **Dataset Example**: `gaming_transactions` database with `item_transactions` table (transaction_id, user_id, item_name, amount_jpy, etc.)

### Cloud Run Jobs Workflow
```
Raw BigQuery Tables (rooms, guests, bookings) → Python Processing Script → Transformed Tables (fact_bookings, agg_room_revenue)
```
- **Location**: `cloudrunjobs/`
- **Container**: Docker image with `python:3.9-slim` base, runs `process_rooms_data.py`
- **Execution**: Cloud Run Job (serverless batch processing)
- **Key Functions**:
  - `create_fact_table()`: Denormalizes bookings data, adds calculated `duration_days` field
  - `create_agg_table()`: Aggregates revenue by room using GROUP BY queries
- **Dataset Assumption**: Script expects pre-existing `rooms_data` dataset with `rooms`, `guests`, `bookings` tables populated

## Critical Conventions & Patterns

### 1. **BigQuery Client Usage** (Cloud Run jobs pattern)
- Import: `from google.cloud import bigquery`
- Authentication: Automatic via GCP service account (deployed in Cloud Run context)
- Project inference: `client.project` gets current GCP project
- Schema definition: Use `bigquery.SchemaField()` with REQUIRED modes for dimension tables

### 2. **Data Generation Pattern** (Python scripts)
- **Two-tier approach**: 
  - `generate_*_simple.py`: Zero external dependencies (uses stdlib only)
  - `generate_*.py`: Full Faker/pandas version for richer data
- **Use simple version when**: Dependency conflicts or resource constraints
- **Default seed**: `random.seed(42)` ensures reproducible test data
- **CSV output**: Always saves to `{dataset_name}.csv` in current directory

### 3. **Table Naming Convention**
- **Fact tables**: `fact_*` prefix (detailed transaction records with granular dimensions)
- **Aggregate tables**: `agg_*` prefix (rolled-up metrics by specific dimensions)
- **Raw tables**: No prefix (rooms, guests, bookings)
- **Example fields**: `duration_days` = calculated metric, `total_revenue` = aggregated metric

### 4. **Docker Deployment** (Cloud Run)
- Base image: Python 3.9 slim (production-standard)
- Requirements: Minimal—only `google-cloud-bigquery` for Cloud Run jobs
- Working directory: `/app` (convention)
- Entry point: Direct `CMD ["python", "script.py"]` (no shell wrapper)

## Developer Workflows

### BigQuery Data Generation
```bash
cd BigQuery/BigQuery_Upload
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python generate_transaction_data.py  # Creates gaming_transactions.csv
```

### Cloud Run Job Development & Deployment
```bash
cd cloudrunjobs
# Test locally (requires GCP authentication)
gcloud auth login
gcloud config set project YOUR_PROJECT
python process_rooms_data.py

# Deploy to Cloud Run
docker build -t gcr.io/YOUR_PROJECT/process-rooms:latest .
docker push gcr.io/YOUR_PROJECT/process-rooms:latest
gcloud run jobs create rooms-processor --image gcr.io/YOUR_PROJECT/process-rooms:latest
gcloud run jobs execute rooms-processor
```

### Pre-requisites Checklist
- GCP project with BigQuery API enabled
- `gcloud` CLI authenticated: `gcloud init && gcloud auth login`
- Raw tables must exist before running transformation job (see cloudrunjobs README for SQL setup)
- Docker installed for container builds

## Integration Points & External Dependencies

### BigQuery API
- Used in: Cloud Run jobs script (`process_rooms_data.py`)
- Pattern: Programmatic table creation + data insertion via INSERT queries
- Not used in data generation scripts (data stays local before upload)

### GCS (Google Cloud Storage)
- Referenced in folder name `BigQuery_GCS_Upload/` but not implemented in provided code
- Future pattern: Could upload CSVs to GCS before BigQuery ingestion

### Cloud Run
- Execution environment for `process_rooms_data.py`
- Automatic authentication via service account credentials
- Scales to zero between job executions (cost-efficient)

## Key Files to Understand
- [cloudrunjobs/process_rooms_data.py](cloudrunjobs/process_rooms_data.py) — Core transformation logic with fact/aggregate table creation
- [cloudrunjobs/Dockerfile](cloudrunjobs/Dockerfile) — Production container definition
- [BigQuery/BigQuery_Upload/generate_transaction_data_simple.py](BigQuery/BigQuery_Upload/generate_transaction_data_simple.py) — Example data generation pattern without deps
- [cloudrunjobs/README.md](cloudrunjobs/README.md) — Complete setup with raw data SQL scripts

## Common Tasks for Agents

1. **Add new data generator**: Copy `generate_*_simple.py` pattern; use stdlib CSV module + random for data
2. **Extend Cloud Run job**: Add new functions like `create_fact_table()`; update schema fields; use `DATE_DIFF`, `COUNT()` for calculations
3. **Debug BigQuery queries**: All queries run via `client.query().result()`; check GCP project config and dataset permissions
4. **Update container**: Modify `requirements.txt` (add packages), rebuild image, push to registry
5. **Schema migration**: Define new `SchemaField` list, call `create_table(exists_ok=True)`, populate via INSERT

## Patterns to Avoid
- ❌ Storing credentials in code (use GCP service accounts)
- ❌ Hardcoding project IDs (use `client.project` inference)
- ❌ Large data generation in memory (stream to CSV)
- ❌ Mixing data generation with transformation (keep separate for modularity)
