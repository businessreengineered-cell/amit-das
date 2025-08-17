# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc wget curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Render expects traffic on 10000)
EXPOSE 10000

# Start the app (Flask/FastAPI compatible)
CMD ["sh", "-c", "if [ -f app.py ]; then python app.py; else uvicorn app:app --host 0.0.0.0 --port 10000; fi"]
