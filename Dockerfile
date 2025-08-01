FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directory for temporary video storage
RUN mkdir -p temp_videos

# Expose port for FastAPI
EXPOSE 8001

# Start the FastAPI application
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"] 