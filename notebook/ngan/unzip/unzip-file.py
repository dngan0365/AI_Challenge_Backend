from google.cloud import storage
from zipfile import ZipFile, is_zipfile
import io
import os
import requests
from google.oauth2 import service_account
from google.cloud import storage

key_json_path = "../../../service-account.json"

credentials = service_account.Credentials.from_service_account_file(key_json_path)

storage_client = storage.Client(credentials=credentials)

def unzip_gcs_file(event, context=None):
    bucket_name = event['bucket']
    zip_path = event['name']

    # Only process .zip files
    if not zip_path.lower().endswith(".zip"):
        print(f"Skipping non-zip file: {zip_path}")
        return

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(zip_path)

    # Download zip into memory
    zip_bytes = io.BytesIO(blob.download_as_bytes())

    if is_zipfile(zip_bytes):
        with ZipFile(zip_bytes, 'r') as myzip:
            zip_base = os.path.splitext(os.path.basename(zip_path))[0]  
            # e.g. raw_zips/myfile.zip → myfile

            for filename in myzip.namelist():
                data = myzip.read(filename)

                # Always write to dataset/unzips/<zip_name>/<filename>
                new_blob_path = f"dataset/unzips/{zip_base}/{filename}"

                new_blob = bucket.blob(new_blob_path)
                new_blob.upload_from_string(data)

                print(f"Extracted {filename} → gs://{bucket_name}/{new_blob_path}")
    else:
        print(f"File {zip_path} is not a valid zip archive.")

if __name__ == "__main__":
    bucket = storage_client.bucket("test-video-retrieval")

    # Iterate through all .zip files in dataset/raw_zips/
    for blob in bucket.list_blobs(prefix="dataset/raw_zips/"):
        if blob.name.endswith(".zip"):
            print(f"Processing {blob.name}")
            unzip_gcs_file({"bucket": bucket.name, "name": blob.name})
