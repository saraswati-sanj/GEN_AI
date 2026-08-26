# Dockerfile for NutriLens AI FastAPI Backend & Frontend
# Production Ready for Render Free Tier (512MB RAM Limit)

FROM python:3.10-slim

# System dependencies for Barcode scanning (zbar) and Computer Vision (OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install lightweight PyTorch CPU build
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, knowledge base, frontend, and notebooks
COPY backend /app/backend
COPY frontend /app/frontend
COPY knowledge_base /app/knowledge_base
COPY notebooks /app/notebooks

# Resource and thread limits for strict 512MB memory envelope
ENV OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    PYTHONPATH=/app/backend \
    PORT=10000

WORKDIR /app/backend

# Pre-index vector knowledge base at build time
RUN python scripts/ingest_knowledge.py --reset

# Expose default Render port
EXPOSE 10000

# Start server bound to dynamic Render $PORT with 1 single worker to preserve RAM
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
