"""
NutriLens AI — Main FastAPI Application
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.scan import router as scan_router
from app.api.v1.endpoints.history import router as history_router
from app.services.vector_store import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nutrilens.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and Shutdown Lifecycle events."""
    logger.info("Initializing NutriLens AI Backend...")
    
    # 1. Initialize Database tables
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # 2. Check Vector Store initialization
    try:
        count = vector_store.collection.count()
        logger.info(f"Vector Store initialized with {count} chunks in ChromaDB.")
        if count == 0:
            logger.info("Knowledge collection is empty. Running background knowledge ingestion...")
            from scripts.ingest_knowledge import run_ingestion
            run_ingestion(reset=False)
    except Exception as e:
        logger.warning(f"Vector Store auto-check notice: {e}")

    yield
    logger.info("Shutting down NutriLens AI Backend.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Generative AI Food Barcode Health & RAG Risk Assessment Application",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS
if "*" not in origins:
    origins.extend(["http://localhost", "http://127.0.0.1", "*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development & deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 Routers
app.include_router(users_router, prefix="/api/v1")
app.include_router(scan_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "chroma_chunks": vector_store.collection.count() if hasattr(vector_store, 'collection') else 0,
    }

# Mount Frontend static files if frontend folder exists
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
