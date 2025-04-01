import os
import json
import functions_framework
import requests

@functions_framework.http
def main():
    """Fetches hourly temperature data for Bangkok and returns it as JSON.
    
    Args:
        request: HTTP request object.
        
    Returns:
        JSON response containing the hourly temperature data.
    """

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
        print(f"API call success")
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

        # Example usage
        # bucket_name = "zambara"
        # destination_blob_name = "bkk_weather.json"

        # upload_to_gcs(bucket_name, destination_blob_name, response_data)

        # Return JSON response
        return (json.dumps(response_data), 200, {'Content-Type': 'application/json'})

    else:
        # Handle API failure
        error_response = {"error": f"API call failed with status code {response.status_code}"}
        return (json.dumps(error_response), response.status_code, {'Content-Type': 'application/json'})