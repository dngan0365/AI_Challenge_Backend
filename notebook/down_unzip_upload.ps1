# === CONFIGURATION ===
$bucket = "gs://test-video-retrieval"
$rawFolder = "dataset/raw_zips"
$outFolder = "dataset/unzips_b2"

# Danh sách file cần tải về: "Tên file" = "URL"
$files = @{
    # "Videos_K02.zip" = "https://aic-data.ledo.io.vn/Videos_K02.zip"
    # "Videos_K04.zip" = "https://aic-data.ledo.io.vn/Videos_K04.zip"
    # "Videos_K06.zip" = "https://aic-data.ledo.io.vn/Videos_K06.zip"
    # "Videos_K07.zip" = "https://aic-data.ledo.io.vn/Videos_K07.zip"
    # "Videos_K09.zip" = "https://aic-data.ledo.io.vn/Videos_K09.zip"
    # "Videos_K11.zip" = "https://aic-data.ledo.io.vn/Videos_K11.zip"
    # "Videos_K13.zip" = "https://aic-data.ledo.io.vn/Videos_K13.zip"
    # "Videos_K19.zip" = "https://aic-data.ledo.io.vn/Videos_K19.zip"
    # "Videos_K20.zip" = "https://aic-data.ledo.io.vn/Videos_K20.zip"
    # "Keyframes_K02.zip" = "https://aic-data.ledo.io.vn/Keyframes_K02.zip"
    # "Keyframes_K08.zip" = "https://aic-data.ledo.io.vn/Keyframes_K08.zip"
    # "Keyframes_K10.zip" = "https://aic-data.ledo.io.vn/Keyframes_K10.zip"
    # "Keyframes_K11.zip" = "https://aic-data.ledo.io.vn/Keyframes_K11.zip"
    "Keyframes_K12.zip" = "https://aic-data.ledo.io.vn/Keyframes_K12.zip"
    # "Keyframes_K14.zip" = "https://aic-data.ledo.io.vn/Keyframes_K14.zip"
    # "Keyframes_K15.zip" = "https://aic-data.ledo.io.vn/Keyframes_K15.zip"
    # "Keyframes_K17.zip" = "https://aic-data.ledo.io.vn/Keyframes_K17.zip"
}

# Thư mục tạm để xử lý
$tempDir = Join-Path -Path $env:TEMP -ChildPath "gcs_download_unzip"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Hàm tải với retry nếu lỗi
function Download-FileWithRetry {
    param (
        [string]$url,
        [string]$outputPath,
        [int]$maxRetries = 5
    )
    $attempt = 0
    while ($attempt -lt $maxRetries) {
        $attempt++
        Write-Host "Attempt ${attempt}: Downloading ${url}..."
        & curl.exe -C - -L "${url}" -o "${outputPath}"

        # Kiểm tra dung lượng thực tế vs dung lượng server
        try {
            $head = Invoke-WebRequest -Uri "${url}" -Method Head
            $contentLength = [int64]$head.Headers["Content-Length"]
            $fileSize = (Get-Item "${outputPath}").Length

            if ($fileSize -eq $contentLength) {
                Write-Host "Download successful: ${outputPath}"
                return $true
            } else {
                Write-Host "Download incomplete (${fileSize}/${contentLength}). Retrying..."
                Remove-Item "${outputPath}" -Force
            }
        } catch {
            Write-Host "Error checking file size. Retrying..."
            if (Test-Path "${outputPath}") { Remove-Item "${outputPath}" -Force }
        }
    }
    throw "Failed to download ${url} after ${maxRetries} attempts."
}

foreach ($file in $files.Keys) {
    $url = $files[$file]
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file)
    $localZipPath = Join-Path $tempDir $file
    $localUnzipDir = Join-Path $tempDir $fileName

    Write-Host "`n=== Processing ${file} ==="

    # 1. Download ZIP từ URL với retry
    Download-FileWithRetry -url $url -outputPath $localZipPath

    # 2. Unzip file local
    Write-Host "Unzipping ${file}..."
    New-Item -ItemType Directory -Path $localUnzipDir | Out-Null
    Expand-Archive -LiteralPath "${localZipPath}" -DestinationPath "${localUnzipDir}" -Force

    # 3. Upload folder unzip lên GCS/unzips
    $gcsUnzipPath = "${bucket}/${outFolder}/${fileName}/"
    Write-Host "Uploading unzipped content to ${gcsUnzipPath}..."
    & gsutil -m cp -r "${localUnzipDir}/*" $gcsUnzipPath

    # 4. Cleanup
    Write-Host "Cleaning up local temp files..."
    Remove-Item "${localZipPath}" -Force
    Remove-Item "${localUnzipDir}" -Recurse -Force
}

Write-Host "`nAll files processed successfully."
