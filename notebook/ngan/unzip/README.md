# Unzip Job: GCP Cloud Build Docker Image

This directory contains the resources to build a Docker image for unzipping large datasets in Google Cloud Platform (GCP) using Cloud Build.

## Overview

This image is designed to:
- Download .zip files from Google Cloud Storage (GCS)
- Unzip them efficiently inside a container
- Upload the extracted files back to GCS

This is useful for handling large datasets that cannot be unzipped directly in GCS or in-memory (e.g., 100GB+ archives).

## Usage

### 1. Build the Docker Image

Use Google Cloud Build to build and push the image to Google Container Registry (GCR):

```sh
gcloud builds submit --tag gcr.io/<YOUR_PROJECT_ID>/unzip-job
```

Replace `<YOUR_PROJECT_ID>` with your actual GCP project ID.

### 2. Run the Image

You can run the image on Google Cloud Run, Vertex AI Workbench, or a Compute Engine VM. Pass environment variables or arguments as needed to specify:
- The GCS bucket and path for input .zip files
- The destination GCS bucket/path for extracted files

Example (pseudo-code):

```sh
docker run -e INPUT_GCS=gs://your-bucket/raw_zips/Keyframes_L21.zip \
           -e OUTPUT_GCS=gs://your-bucket/unzipped/ \
           gcr.io/<YOUR_PROJECT_ID>/unzip-job
```

### 3. Example Workflow

1. Upload your .zip files to GCS (e.g., `gs://your-bucket/raw_zips/`).
2. Use this image to download, unzip, and upload the contents to `gs://your-bucket/unzipped/`.

## Files
- `Dockerfile`: Defines the environment and entrypoint for the unzip job.
- `main.py` (or similar): Python script to handle download, unzip, and upload logic.
- `requirements.txt`: Python dependencies.

## Requirements
- Google Cloud SDK (`gcloud`)
- Permissions to use Cloud Build and access GCS buckets

## Tips
- For very large files, use a machine with sufficient disk and memory.
- Clean up temporary files after processing to avoid disk space issues.
- Use `gsutil -m` for parallel uploads if scripting outside Docker.

---

For questions or issues, contact the project maintainer.

## 1️⃣ Confirm active account

Check which account gcloud is actually using:

gcloud auth list


You should see something like:

* dngan0365@gmail.com


If not, switch:

 config set account dngan0365@gmail.com

## 2️⃣ Check project configuration

Ensure gcloud is pointing to the right project:

gcloud config get-value project


If it’s not:

gcloud config set project gen-lang-client-0974620078

## 3️⃣ Enable required APIs

Even though Cloud Build prompted to enable, sometimes other APIs are needed:

gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com

## 4️⃣ Authenticate with Application Default Credentials

Sometimes the CLI uses your user credentials instead of service account permissions. You can try:

gcloud auth application-default login


This ensures gcloud builds submit can access the project resources.

## 5️⃣ Retry build
```bash
gcloud builds submit --tag gcr.io/gen-lang-client-0974620078/unzip-job
```
If this still fails, a common workaround is to build the Docker image locally and push it directly to Container Registry:
```bash
docker build -t gcr.io/gen-lang-client-0974620078/unzip-job .
docker push gcr.io/gen-lang-client-0974620078/unzip-job
```

Then create the Cloud Run Job using that image.