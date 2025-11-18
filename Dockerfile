# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GCP_PROJECT=ps-deals-tracker
ENV USE_MOCK_ADAPTER=false

# Run the application
CMD ["python", "-m", "app.main"]
