#!/usr/bin/env python3
"""
Cloud Run Jobs Data Engineering Demo Script

This script demonstrates processing data in BigQuery for a GCP Cloud Run Job.
It assumes the 'rooms_data' dataset and raw tables (rooms, guests, bookings) already exist with data.
It creates a fact table and an aggregate table from the raw data.
"""

from google.cloud import bigquery
import os

# Set up BigQuery client
client = bigquery.Client()

# Dataset name
dataset_name = 'rooms_data'
dataset_id = f"{client.project}.{dataset_name}"

def create_fact_table():
    """Create the fact table: fact_bookings."""
    fact_schema = [
        bigquery.SchemaField("booking_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("guest_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("room_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("check_in_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("check_out_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("total_amount", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("duration_days", "INTEGER", mode="REQUIRED"),
    ]
    fact_table_id = f"{dataset_id}.fact_bookings"
    fact_table = bigquery.Table(fact_table_id, schema=fact_schema)
    client.create_table(fact_table, exists_ok=True)
    print(f"Table {fact_table_id} created.")

    # Insert data into fact table
    query = f"""
    INSERT INTO `{fact_table_id}`
    SELECT
        b.booking_id,
        b.guest_id,
        b.room_id,
        b.check_in_date,
        b.check_out_date,
        b.total_amount,
        DATE_DIFF(b.check_out_date, b.check_in_date, DAY) as duration_days
    FROM `{dataset_id}.bookings` b
    """
    client.query(query).result()
    print("Inserted data into fact_bookings table.")

def create_agg_table():
    """Create the aggregate table: agg_room_revenue."""
    agg_schema = [
        bigquery.SchemaField("room_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_bookings", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_revenue", "FLOAT", mode="REQUIRED"),
    ]
    agg_table_id = f"{dataset_id}.agg_room_revenue"
    agg_table = bigquery.Table(agg_table_id, schema=agg_schema)
    client.create_table(agg_table, exists_ok=True)
    print(f"Table {agg_table_id} created.")

    # Insert data into agg table
    query = f"""
    INSERT INTO `{agg_table_id}`
    SELECT
        room_id,
        COUNT(*) as total_bookings,
        SUM(total_amount) as total_revenue
    FROM `{dataset_id}.bookings`
    GROUP BY room_id
    """
    client.query(query).result()
    print("Inserted data into agg_room_revenue table.")

def main():
    print("Starting Cloud Run Jobs Data Engineering Demo...")
    create_fact_table()
    create_agg_table()
    print("Demo completed successfully!")

if __name__ == "__main__":
    main()