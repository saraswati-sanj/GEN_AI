# Dockerfile for NutriLens AI FastAPI Backend & Frontend

FROM python:3.10-slim

# Install system dependencies (zbar barcode library, libgl1 for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and frontend code
COPY backend /app/backend
COPY frontend /app/frontend

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

ENV PYTHONPATH=/app/backend

# Run knowledge base ingestion and start Uvicorn server (respects Render $PORT)
CMD ["sh", "-c", "python scripts/ingest_knowledge.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
