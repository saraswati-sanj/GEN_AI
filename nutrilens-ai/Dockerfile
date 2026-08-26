# Dockerfile for NutriLens AI FastAPI Backend & Frontend
# Optimized for low-memory cloud runtimes (e.g. Render Free Tier 512MB RAM)

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

# 1. Install lightweight PyTorch CPU-only (cuts RAM from 650MB -> 120MB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install application Python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy backend code, knowledge base, frontend code, and notebooks
COPY backend /app/backend
COPY frontend /app/frontend
COPY knowledge_base /app/knowledge_base
COPY notebooks /app/notebooks

# Configure single-thread BLAS/PyTorch to stay strictly within 512MB RAM
ENV OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    PYTHONPATH=/app/backend

# Set working directory to backend
WORKDIR /app/backend

# Pre-build ChromaDB vector index during Docker build stage
RUN python scripts/ingest_knowledge.py --reset

# Expose port
EXPOSE 8000

# Start Uvicorn directly at runtime with fast startup and low memory footprint
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
