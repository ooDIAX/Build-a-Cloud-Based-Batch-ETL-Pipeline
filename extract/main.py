import os
import json
import requests
from flask import Flask, request, jsonify
from google.cloud import storage
from datetime import datetime

app = Flask(__name__)

def upload_to_gcs(bucket_name, destination_blob_name, data):
    """Uploads JSON data to GCS with error handling."""
    try:
        print("Start upload to GCS")
        
        # Initialize the GCS client (uses Cloud Run service account)
        client = storage.Client()
        
        # Get the GCS bucket
        bucket = client.bucket(bucket_name)
        
        # Create a blob (object) in the bucket
        blob = bucket.blob(destination_blob_name)
        
        # Convert data to JSON format and upload
        blob.upload_from_string(json.dumps(data), content_type='application/json')
        
        print(f"Data uploaded to gs://{bucket_name}/{destination_blob_name}")
    
    except storage.exceptions.GoogleCloudError as e:
        # Catch Google Cloud storage specific errors
        print(f"Google Cloud Storage error: {e}")
    
    except json.JSONDecodeError as e:
        # Handle errors that might occur while converting to JSON
        print(f"JSON encoding error: {e}")
    
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")


@app.route("/", methods=["GET"])
def main():
    return jsonify({"test": "works"}), 200
    """Fetches hourly temperature data for Bangkok and uploads it to GCS."""

    # API endpoint and parameters for Bangkok
    API_URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 13.7563,  # Bangkok latitude
        "longitude": 100.5018,  # Bangkok longitude
        "hourly": "temperature_2m",
        "timezone": "Asia/Bangkok"
    }

    # Step 1: Make API Request
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()  # Convert response to JSON

        # Step 2: Extract relevant data
        timestamps = data["hourly"]["time"]
        temperatures = data["hourly"]["temperature_2m"]

        # Step 3: Structure response data
        response_data = {
            "city": "Bangkok",
            "latitude": params["latitude"],
            "longitude": params["longitude"],
            "hourly_temperatures": [
                {"timestamp": t, "temperature": temp}
                for t, temp in zip(timestamps, temperatures)
            ]
        }

        bucket_name = "prujina"
        destination_blob_name = f"Build-a-Cloud-Based-Batch-ETL-Pipeline/bkk_weather.json"

        upload_to_gcs(bucket_name, destination_blob_name, response_data)

        return {"status": "success", "blob_name": destination_blob_name, "data": response_data}, 200

    else:
        return jsonify({"error": f"API call failed with status code {response.status_code}"}), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
