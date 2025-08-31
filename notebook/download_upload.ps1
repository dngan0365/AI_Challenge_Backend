# Requires: gsutil (from Google Cloud SDK) and curl
# Run in PowerShell: .\download_upload.ps1

$files = @{
    "Videos_L25_a.zip"= "https://aic-data.ledo.io.vn/Videos_L25_a.zip"
}

$bucket = "gs://test-video-retrieval/dataset/raw_zips"

foreach ($file in $files.Keys) {
    $url = $files[$file]
    $fullPath = Join-Path -Path (Get-Location) -ChildPath $file

    # Remove local file if exists
    if (Test-Path $fullPath) {
        Write-Host "File $file exists locally. Removing old file..."
        Remove-Item $fullPath -Force
    }

    # Download with resume
    Write-Host "Downloading $file..."
    & curl.exe -C - -L $url -o $fullPath

    # Check and remove old file on GCS
    Write-Host "Checking if $file exists on GCS..."
    try {
        & gsutil ls "$bucket/$file" | Out-Null
        Write-Host "File $file exists on GCS. Removing old file..."
        & gsutil rm "$bucket/$file"
    } catch {
        Write-Host "File $file does not exist on GCS."
    }

    # Upload new file
    Write-Host "Uploading $file to $bucket..."
    & gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" cp $fullPath "$bucket/"

    # Remove local copy after upload
    Remove-Item $fullPath -Force
}
