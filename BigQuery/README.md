# BigQuery

This folder contains examples and exercises for Google Cloud BigQuery, a serverless, highly scalable data warehouse.

## Contents

- **BigQuery_Upload/**: Examples of uploading data to BigQuery
  - Sample transaction data generation
  - Data upload scripts
  - Virtual environment setup

## Key BigQuery Concepts Covered

- Data ingestion and loading
- Schema design
- Query optimization
- Partitioning and clustering
- Data types and functions
- Security and access control

## Getting Started

1. Navigate to the specific subfolder
2. Follow the README instructions for setup
3. Run the provided scripts

## Useful BigQuery Commands

```bash
# List datasets
bq ls

# List tables in a dataset
bq ls dataset_name

# Query a table
bq query "SELECT * FROM project.dataset.table LIMIT 10"

# Create a dataset
bq mk dataset_name

# Create a table with schema
bq mk --table project.dataset.table schema.json
```
