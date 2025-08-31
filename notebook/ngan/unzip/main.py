import os
import zipfile
from google.cloud import storage

# Read environment variables
BUCKET = os.environ["BUCKET"]
RAW_ZIPS = os.environ.get("RAW_ZIPS", "dataset/raw_zips")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "dataset/unzips")

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(BUCKET)

# List all .zip files in the bucket under RAW_ZIPS
blobs = bucket.list_blobs(prefix=RAW_ZIPS)

for blob in blobs:
    if blob.name.endswith(".zip"):
        local_zip = "/tmp/" + os.path.basename(blob.name)
        out_dir = "/tmp/unzipped"

        print(f"Downloading {blob.name} to {local_zip}...")
        blob.download_to_filename(local_zip)

        os.makedirs(out_dir, exist_ok=True)

        print(f"Unzipping {local_zip}...")
        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            zip_ref.extractall(out_dir)

        # Upload each extracted file back to GCS
        for root, _, files in os.walk(out_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                # GCS path: OUT_PREFIX/filename
                gcs_path = os.path.join(OUT_PREFIX, file)
                blob_out = bucket.blob(gcs_path)
                print(f"Uploading {local_file_path} to {gcs_path}...")
                blob_out.upload_from_filename(local_file_path)
