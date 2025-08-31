$bucket = "gs://test-video-retrieval"
$rawFolder = "dataset/raw_zips"
$outFolder = "dataset/unzips"

# Files you want to process
$targetFiles = @(
    "objects-aic25-b1.zip"
)

# Temporary folder for processing
$tempDir = Join-Path -Path $env:TEMP -ChildPath "gcs_unzip"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
New-Item -ItemType Directory -Path $tempDir | Out-Null

foreach ($file in $targetFiles) {
    $zipPath = "$bucket/$rawFolder/$file"
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file)
    $localZipPath = Join-Path $tempDir $file
    $localUnzipDir = Join-Path $tempDir $fileName

    Write-Host "`nProcessing $zipPath"

    # Download zip from GCS
    & gsutil cp $zipPath $localZipPath

    # Unzip locally
    New-Item -ItemType Directory -Path $localUnzipDir | Out-Null
    Expand-Archive -LiteralPath $localZipPath -DestinationPath $localUnzipDir -Force

    # Upload unzipped files back to GCS
    $gcsOutPath = "$bucket/$outFolder/$fileName/"
    Write-Host "Uploading unzipped files to $gcsOutPath..."
    & gsutil -m cp -r "$localUnzipDir/*" $gcsOutPath

    # Cleanup local files
    Remove-Item $localZipPath -Force
    Remove-Item $localUnzipDir -Recurse -Force
}

Write-Host "`nSelected GCS zip files processed."
