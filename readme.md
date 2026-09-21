# SLA Monitoring

## GCP Setup: Cloud Storage + Cloud Function (CSV Parser)

Provisions a GCS bucket for incoming service-log CSVs and deploys a Gen2 Cloud Function that parses each file on upload.

> Replace `<PROJECT_ID>` below with your own GCP project ID before running these commands.

### 1. Install gcloud CLI
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl

curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

sudo apt-get update && sudo apt-get install -y google-cloud-cli
gcloud --version
gcloud init
```

### 2. Enable required APIs
```bash
gcloud services enable \
  storage.googleapis.com \
  run.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  eventarc.googleapis.com \
  pubsub.googleapis.com \
  --project=<PROJECT_ID>
```

### 3. Create the bucket
```bash
gcloud storage buckets create gs://service-log-csv-store \
  --location=us-central1 \
  --uniform-bucket-level-access \
  --default-storage-class=STANDARD
```

### 4. Grant IAM permissions
```bash
# GCS service agent (needed to publish Eventarc/Pub-Sub notifications)
gcloud beta services identity create \
  --service=storage.googleapis.com \
  --project=<PROJECT_ID>

# App Engine default service account: read/write access to the bucket
gcloud storage buckets add-iam-policy-binding gs://service-log-csv-store \
  --member="serviceAccount:<PROJECT_ID>@appspot.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Allow publishing to Pub/Sub (trigger delivery)
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:${gcloud storage service-agent --project=<PROJECT_ID>}" \
  --role="roles/pubsub.publisher"
```

### 5. Local development
```bash
cd sla-monitoring/backend/cloud-functions

# Run the function locally for testing
uv run functions-framework --target=parse_csv --debug --port 8001
```

### 6. Deploy the Cloud Function
```bash
# Export dependencies from pyproject.toml to requirements.txt, required by gcloud functions deploy
uv export --no-hashes --format requirements-txt --no-annotate -o requirements.txt

gcloud functions deploy csv-parser \
  --gen2 \
  --runtime=python313 \
  --region=us-central1 \
  --source=. \
  --entry-point=parse_csv \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized,bucket=service-log-csv-store"
```

The function is triggered whenever a new object is finalized (uploaded) in the `service-log-csv-store` bucket.
