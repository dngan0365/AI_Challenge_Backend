FROM python:3.11-slim

WORKDIR /app

# Install unzip for Python (not strictly needed, but safe)
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python script
COPY main.py .

# Set environment variables (can override with Cloud Run job)
ENV BUCKET=test-video-retrieval
ENV OUT_PREFIX=dataset/unzips
ENV RAW_ZIPS=dataset/raw_zips

# Run the job
CMD ["python", "main.py"]
