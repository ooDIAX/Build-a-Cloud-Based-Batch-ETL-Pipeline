import os
import json
import requests
import functions_framework

@functions_framework.http
def main(request):
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

        # Return JSON response
        return (json.dumps(response_data), 200, {'Content-Type': 'application/json'})

    else:
        # Handle API failure
        error_response = {"error": f"API call failed with status code {response.status_code}"}
        return (json.dumps(error_response), response.status_code, {'Content-Type': 'application/json'})
