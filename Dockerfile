FROM python:3.12-slim

# Tạo thư mục làm việc
WORKDIR /app

# Copy file requirements vào image
COPY requirements.txt ./

# Cài đặt các package cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào image
COPY . .

# Mở port cho FastAPI
EXPOSE 8000

# Chạy ứng dụng FastAPI bằng uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]