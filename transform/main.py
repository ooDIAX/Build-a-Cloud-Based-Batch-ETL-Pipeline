from flask import Flask, request
from google.cloud import bigquery, storage
import json

app = Flask(__name__)

# Initialize clients
bq_client = bigquery.Client()
storage_client = storage.Client()

# Configuration (replace with your values)
PROJECT_ID = "qvegriala"
DATASET_ID = "qvegriala.bangkok_weather"
TABLE_ID = "qvegriala.bangkok_weather.bangkok_weather"
BUCKET_NAME = "prujina"
SOURCE_FILE = "Build-a-Cloud-Based-Batch-ETL-Pipeline/bkk_weather.json"

# Define the schema explicitly (optional, can use autodetect instead)
SCHEMA = [
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("temperature", "FLOAT"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("latitude", "FLOAT"),
    bigquery.SchemaField("longitude", "FLOAT"),
]

@app.route("/", methods=["POST"])
def load_to_bigquery():
    try:
        # Get the table reference
        table_ref = bq_client.dataset(DATASET_ID).table(TABLE_ID)
        
        # Create the table if it doesn't exist
        table = bigquery.Table(table_ref, schema=SCHEMA)
        try:
            bq_client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"Table creation failed or already exists: {e}")

        # Download JSON from GCS
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(SOURCE_FILE)
        json_data = json.loads(blob.download_as_string())

        # Transform the data: flatten hourly_temperatures into rows
        rows_to_insert = []
        city = json_data["city"]
        latitude = json_data["latitude"]
        longitude = json_data["longitude"]
        
        for hourly in json_data["hourly_temperatures"]:
            row = {
                "city": city,
                "temperature": hourly["temperature"],
                "timestamp": hourly["timestamp"],
                "latitude": latitude,
                "longitude": longitude
            }
            rows_to_insert.append(row)

        # Insert rows into BigQuery
        errors = bq_client.insert_rows_json(table_ref, rows_to_insert)
        
        if errors:
            return f"Errors occurred: {errors}", 500
        
        return f"Loaded {len(rows_to_insert)} rows into {DATASET_ID}.{TABLE_ID}", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)