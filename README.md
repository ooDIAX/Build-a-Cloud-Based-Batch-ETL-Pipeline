# Weather Data Pipeline

This project implements a two-stage data pipeline using Google Cloud Run to fetch weather data and load it into BigQuery:
1. `extract`: Fetches hourly weather data from an API (e.g., OpenWeatherMap) and stores it as JSON in Google Cloud Storage (GCS).
2. `transform`: Reads the JSON from GCS, transforms it, and loads it into a BigQuery table.


## Prerequisites

- Google Cloud Project: With billing enabled.
- GCP Services: Cloud Run, Cloud Storage, BigQuery, and Cloud Build enabled.
- Tools:
  - Google Cloud SDK (`gcloud`) installed.
  - Docker installed (for local testing).


- API Key: An OpenWeatherMap API key (or equivalent) for the `extract` service.

## Setup

### 1. Configure Environment

- Project ID: Replace `your-project-id` in all files with your Google Cloud Project ID.
- GCS Bucket: Create a bucket (e.g., `your-bucket`) and note its name.
- BigQuery Dataset: Create a dataset (e.g., `bangkok_weather`) in BigQuery.
### 2. Service Account Permissions

The Cloud Run service account (e.g., `123456-compute@developer.gserviceaccount.com`) needs:
- `roles/storage.objectViewer`: To read from GCS.
- `roles/bigquery.dataEditor`: To write to BigQuery.

Assign roles:
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:123456-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:123456-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

### 3. Update Configuration

- extract/main.py:
  - Set `BUCKET_NAME = "your-bucket"`.
  - Set `API_KEY = "your-openweathermap-api-key"`.
  - Adjust the API endpoint or city as needed.
- transform/main.py:
  - Set `PROJECT_ID = "your-project-id"`.
  - Set `DATASET_ID = "bangkok_weather"`.
  - Set `TABLE_ID = "hourly_weather"`.
  - Set `BUCKET_NAME = "your-bucket"`.
  - Set `SOURCE_FILE = "weather_data.json"`.
    ## Deployment

### Deploy `extract` Service

gcloud run deploy weather-extract \
  --source extract \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

- Triggers weather data fetch and saves to GCS when called via POST.

### Deploy `transform` Service

gcloud run deploy weather-transform \
  --source transform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

- Loads JSON from GCS into BigQuery when called via POST.

  ## Usage

### Trigger the Pipeline

1. Run `extract`:
curl -X POST https://weather-extract-abc123-uc.a.run.app
   - Replace the URL with your `weather-extract` service URL.
   - Saves weather data to `gs://your-bucket/weather_data.json`.

2. Run `transform`:
curl -X POST https://weather-transform-abc123-uc.a.run.app
   - Replace the URL with your `weather-transform` service URL.
   - Loads data into `your-project-id.bangkok_weather.hourly_weather`.
  
   ## Local Testing

1. Test `extract`:
cd extract
docker build -t test-extract .
docker run -p 8080:8080 test-extract
curl -X POST http://localhost:8080

2. Test `transform`:
cd transform
docker build -t test-transform .
docker run -p 8080:8080 test-transform
curl -X POST http://localhost:8080

## Troubleshooting

- Service Unavailable: Check Cloud Run logs (`gcloud run services logs tail --service weather-transform --region us-central1`).
- No Data in BigQuery: Verify GCS file exists (`gsutil ls gs://your-bucket/weather_data.json`) and logs for errors.
- Permissions: Ensure the service account has the required roles.

## Data Schema

The BigQuery table (`bangkok_weather.hourly_weather`) has the following schema:
Field       | Type      | Description
------------|-----------|------------------------------
city        | STRING    | City name (e.g., "Bangkok")
temperature | FLOAT     | Hourly temperature (°C)
timestamp   | TIMESTAMP | Date and time of reading
latitude    | FLOAT     | Latitude coordinate
longitude   | FLOAT     | Longitude coordinate
