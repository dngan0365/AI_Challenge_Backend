# main.py
from fastapi import FastAPI, Request
from google.oauth2 import service_account
from google.cloud import storage
from zipfile import ZipFile, is_zipfile
import io
import os

# Load credentials (best: from env var GOOGLE_APPLICATION_CREDENTIALS)
key_json_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")

credentials = service_account.Credentials.from_service_account_file(key_json_path)
storage_client = storage.Client(credentials=credentials)

app = FastAPI()

@app.post("/unzip")
async def unzip_gcs_file(request: Request):
    body = await request.json()
    bucket_name = body["bucket"]
    zip_path = body["name"]

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(zip_path)
    zip_bytes = io.BytesIO(blob.download_as_bytes())

    if is_zipfile(zip_bytes):
        with ZipFile(zip_bytes, "r") as myzip:
            for filename in myzip.namelist():
                data = myzip.read(filename)
                new_blob = bucket.blob(f"{zip_path.rstrip('.zip')}/{filename}")
                new_blob.upload_from_string(data)
                print(f"Extracted {filename} → gs://{bucket_name}/{zip_path.rstrip('.zip')}/{filename}")

    return {"status": "done", "bucket": bucket_name, "zip": zip_path}
