# BigQuery GCS Upload

This folder contains scripts for uploading data to BigQuery via Google Cloud Storage (GCS), specifically focused on passenger inflight purchase data for 2025.

## Dataset and Table Information

- **Dataset Name**: `airline_purchases`
- **Table Name**: `inflight_purchases`
- **Storage**: Google Cloud Storage bucket

## Setup Instructions

### 1. Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Upgrade pip and install wheel
pip install --upgrade pip wheel

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com

# Create GCS bucket (replace with your bucket name)
gsutil mb gs://your-bucket-name
```

### 3. Run the Data Generation Script

```bash
python generate_inflight_purchase_data.py
```

This will generate two JSON files with nested passenger inflight purchase data.

## Data Structure

The generated JSON files contain nested data with the following structure:

- `passenger_id`: Unique passenger identifier
- `flight_info`: Nested object containing flight details
- `purchase_history`: Array of purchase objects
- `personal_info`: Nested object with passenger demographics
- `loyalty_status`: Passenger loyalty program information
- `payment_methods`: Array of payment methods
- `preferences`: Nested object with passenger preferences
- `metadata`: Additional metadata about the record

## Next Steps

1. Upload the generated JSON files to your GCS bucket
2. Create dataset: `airline_purchases`
3. Create table: `inflight_purchases` with JSON schema
4. Load data from GCS to BigQuery
5. Practice BigQuery JSON functions and nested data queries
