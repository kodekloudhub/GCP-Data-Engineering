# GCP Cloud Run Jobs Data Engineering Demo

This demo showcases a simple data engineering pipeline using Google Cloud Platform's Cloud Run Jobs. The pipeline reads data from BigQuery, processes it, and writes results back to BigQuery.

## Overview

**Why Cloud Run Jobs?** Cloud Run Jobs are ideal for batch processing and data engineering tasks because they allow you to run containerized workloads on-demand without managing servers. They scale automatically, support advanced features like GPU acceleration and parallelism for compute-intensive tasks, and integrate seamlessly with GCP services like BigQuery. This makes them perfect for ETL pipelines, data transformations, and scheduled data processing jobs.

The demo assumes a `rooms_data` dataset with 3 raw tables (`rooms`, `guests`, `bookings`) already exist with data.
The Cloud Run Job processes this data to create:
- 1 fact table: `fact_bookings` (detailed booking records with calculated duration)
- 1 aggregate table: `agg_room_revenue` (summary of bookings and revenue per room)

The Python script runs inside a Docker container deployed as a Cloud Run Job.

## Prerequisites

1. **Google Cloud Project with BigQuery API enabled**: A GCP project is required to host resources. BigQuery API must be enabled to interact with BigQuery datasets and tables.
2. **Install Google Cloud CLI (gcloud)**: The gcloud CLI is essential for authenticating with GCP, managing resources, and deploying containers. Run these commands in your terminal (Ubuntu/Debian-based systems):
   ```bash
   sudo apt-get update
   sudo apt-get install apt-transport-https ca-certificates gnupg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
   sudo apt-get update && sudo apt-get install google-cloud-sdk
   ```
   After installation, initialize with: `gcloud init` (this sets up your default project and region).
3. **gcloud CLI authenticated**: Authentication is needed to access GCP services securely.
   ```bash
   gcloud auth login
   gcloud config set project kodekloud-gcp-training
   ```
4. **Docker installed locally**: Docker is required to build and push container images to GCP registries.
5. **Permissions to create datasets/tables in BigQuery and push to Container Registry/Artifact Registry**: Ensure your account has the necessary IAM roles (e.g., BigQuery Admin, Storage Admin) to perform these operations.

## Setting up Raw Data

**Why set up raw data first?** The Cloud Run Job focuses on processing (transforming raw data into fact and aggregate tables). Raw data setup simulates an ingestion step, ensuring the job has data to work with. This separation demonstrates a typical ETL pipeline where ingestion and processing are decoupled.

Before running the Cloud Run Job, create the dataset and raw tables with data. You can do this via BigQuery Console or CLI.

### Create Dataset
```sql
CREATE SCHEMA `kodekloud-gcp-training.rooms_data`
OPTIONS (
  location = 'US'  -- Choose a location close to your users for better performance
);
```

### Create Tables
```sql
-- Rooms table: Stores room details
CREATE TABLE `kodekloud-gcp-training.rooms_data.rooms` (
  room_id STRING NOT NULL,        -- Unique identifier for each room
  room_type STRING NOT NULL,      -- Type of room (e.g., Single, Double, Suite)
  capacity INT64 NOT NULL,        -- Maximum number of guests
  price_per_night FLOAT64 NOT NULL -- Price per night in USD
);

-- Guests table: Stores guest information
CREATE TABLE `kodekloud-gcp-training.rooms_data.guests` (
  guest_id STRING NOT NULL,       -- Unique identifier for each guest
  name STRING NOT NULL,           -- Full name of the guest
  email STRING NOT NULL,          -- Email address for contact
  phone STRING                    -- Phone number (optional)
);

-- Bookings table: Stores booking transactions
CREATE TABLE `kodekloud-gcp-training.rooms_data.bookings` (
  booking_id STRING NOT NULL,     -- Unique identifier for each booking
  guest_id STRING NOT NULL,       -- References guest who made the booking
  room_id STRING NOT NULL,        -- References the booked room
  check_in_date DATE NOT NULL,    -- Date of check-in
  check_out_date DATE NOT NULL,   -- Date of check-out
  total_amount FLOAT64 NOT NULL   -- Total cost of the booking
);
```

### Insert Sample Data
```sql
-- Insert into rooms
INSERT INTO `kodekloud-gcp-training.rooms_data.rooms` (room_id, room_type, capacity, price_per_night)
VALUES
  ('R001', 'Single', 1, 100.0),
  ('R002', 'Double', 2, 150.0),
  ('R003', 'Suite', 4, 300.0);

-- Insert into guests
INSERT INTO `kodekloud-gcp-training.rooms_data.guests` (guest_id, name, email, phone)
VALUES
  ('G001', 'John Doe', 'john@example.com', '123-456-7890'),
  ('G002', 'Jane Smith', 'jane@example.com', '098-765-4321'),
  ('G003', 'Bob Johnson', 'bob@example.com', '555-123-4567');

-- Insert into bookings
INSERT INTO `kodekloud-gcp-training.rooms_data.bookings` (booking_id, guest_id, room_id, check_in_date, check_out_date, total_amount)
VALUES
  ('B001', 'G001', 'R001', '2023-01-01', '2023-01-03', 200.0),
  ('B002', 'G002', 'R002', '2023-01-02', '2023-01-05', 450.0),
  ('B003', 'G003', 'R003', '2023-01-03', '2023-01-07', 1200.0);
```

## Building and Pushing Docker Image

**Why containerize?** Containers ensure the code runs consistently across environments. Cloud Run Jobs require containerized applications, making Docker essential for packaging dependencies and scripts.

1. **Build the Docker image locally**: This creates a container image with your Python script and dependencies.
   ```bash
   docker build -t gcp-data-eng-demo .
   ```

2. **(Optional for Artifact Registry) Create an Artifact Registry repository**: Artifact Registry is GCP's modern container registry. Creating a repo organizes your images.
   ```bash
   gcloud artifacts repositories create gcp-data-eng-demo-repo \
     --repository-format=docker \
     --location=europe-west1 \
     --project=kodekloud-gcp-training
   ```

3. **Tag the image for GCP**: Tagging prepares the image for upload to GCP registries.
   ```bash
   # For Container Registry (legacy)
   docker tag gcp-data-eng-demo gcr.io/kodekloud-gcp-training/gcp-data-eng-demo:v1

   # For Artifact Registry (recommended for new projects)
   docker tag gcp-data-eng-demo europe-west1-docker.pkg.dev/kodekloud-gcp-training/gcp-data-eng-demo-repo/gcp-data-eng-demo:v1
   ```

4. **Push to GCP**: Upload the image to make it accessible to Cloud Run.
   ```bash
   # Container Registry
   gcloud auth configure-docker
   docker push gcr.io/kodekloud-gcp-training/gcp-data-eng-demo:v1

   # Artifact Registry
   gcloud auth configure-docker europe-west1-docker.pkg.dev
   docker push europe-west1-docker.pkg.dev/kodekloud-gcp-training/gcp-data-eng-demo-repo/gcp-data-eng-demo:v1
   ```

## Setting up Cloud Run Job from GCP Console

**Why use Cloud Run Jobs?** They provide a serverless way to run batch workloads, automatically scaling and handling infrastructure. The console UI makes it easy to configure advanced features without code.

1. **Go to Cloud Run**: Access the GCP Console to create and manage jobs.
2. **Click "Create Job"**: Start the job creation process.
3. **Configure**:
   - **Name**: `gcp-data-eng-demo-job` (unique identifier for the job)
   - **Region**: Choose your preferred region (e.g., europe-west1) for low latency
   - **Container image URL**: Specify the pushed image path
     - Container Registry: `gcr.io/kodekloud-gcp-training/gcp-data-eng-demo:v1`
     - Artifact Registry: `europe-west1-docker.pkg.dev/kodekloud-gcp-training/gcp-data-eng-demo-repo/gcp-data-eng-demo:v1`
   - **Container command**: `python` (overrides default; optional if Dockerfile CMD is set)
   - **Container arguments**: `process_rooms_data.py` (passes script name; optional)
   - **CPU/GPU**: Enable GPU for ML/AI tasks (select type like NVIDIA Tesla T4)
   - **Parallelism**: Set >1 for concurrent instances (e.g., 2-4 for faster processing)
   - **Memory/CPU**: Allocate resources (e.g., 1 GiB RAM, 1 vCPU)
   - **Timeout**: Max runtime (e.g., 10 min)
   - **Service account**: Use one with BigQuery permissions for data access

4. **Click "Create" then "Execute"**: Deploy and run the job immediately.

## Features Demonstrated

- **Container Commands/Args**: Allows customizing the container's entry point and arguments at runtime, enabling flexible job execution without rebuilding images.
- **GPU Usage**: Leverages GPU acceleration for tasks like machine learning or heavy computations, reducing processing time.
- **Parallel Jobs**: Runs multiple instances simultaneously, speeding up batch processing for large datasets.
- **BigQuery Integration**: Seamlessly connects to GCP's data warehouse for reading raw data and writing processed results.
- **Docker Containerization**: Ensures portability and consistency, packaging all dependencies for reliable execution across environments.

## Monitoring

**Why monitor?** Monitoring ensures the job runs successfully, helps debug issues, and provides insights into performance and costs.

After running the job, check:
- **Cloud Run Jobs logs**: View execution details, errors, and output for troubleshooting.
- **BigQuery console**: Verify that new tables were created and populated correctly.
- **Job execution history**: Review metrics like runtime, CPU usage, and parallelism for optimization.

## Querying Results

**Why query results?** Querying validates the data transformation and allows analysis of the processed data.

Once the job completes, query the processed data in BigQuery:

### Fact Table: fact_bookings
This table contains detailed booking records with calculated duration.
```sql
SELECT * FROM `kodekloud-gcp-training.rooms_data.fact_bookings`;
```

### Aggregate Table: agg_room_revenue
This table summarizes bookings and revenue per room.
```sql
SELECT * FROM `kodekloud-gcp-training.rooms_data.agg_room_revenue`;
```

Example query to see total revenue by room:
```sql
-- Query to analyze revenue performance by room, sorted by highest revenue
SELECT room_id, total_bookings, total_revenue
FROM `kodekloud-gcp-training.rooms_data.agg_room_revenue`
ORDER BY total_revenue DESC;
```

## Cleanup

**Why clean up?** Removing unused resources prevents unnecessary costs and keeps your GCP project organized.

- **Delete the Cloud Run Job**: Removes the job definition to avoid clutter. (Skip if the job was not created.)
  ```bash
  # Check if the job exists
  gcloud run jobs list --region=europe-west1 --project=kodekloud-gcp-training | grep gcp-data-eng-demo-job
  
  # If it exists, delete it
  gcloud run jobs delete gcp-data-eng-demo-job --region=europe-west1 --project=kodekloud-gcp-training --quiet
  ```

- **Drop the `rooms_data` dataset in BigQuery**: Deletes all tables and data; use with caution.
  ```bash
  bq rm -r -f kodekloud-gcp-training:rooms_data
  ```

- **Delete the container image from Registry**: Frees up storage space in Container Registry or Artifact Registry.
  - For Container Registry:
    ```bash
    gcloud container images delete gcr.io/kodekloud-gcp-training/gcp-data-eng-demo:v1 --force-delete-tags
    ```
  - For Artifact Registry:
    ```bash
    gcloud artifacts docker images delete europe-west1-docker.pkg.dev/kodekloud-gcp-training/gcp-data-eng-demo-repo/gcp-data-eng-demo:v1
    ```