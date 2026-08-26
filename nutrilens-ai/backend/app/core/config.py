"""
NutriLens AI — Application Settings
Loaded from environment variables / .env file via pydantic-settings.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ─────────────────────────────────────
    APP_NAME: str = "NutriLens AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # ── Gemini ──────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ── PostgreSQL ──────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://nutrilens:nutrilens_password@localhost:5432/nutrilens_db"

    # ── Security ────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_32_CHARS_MIN"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Embedding / ChromaDB ────────────────────
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "nutrilens_knowledge"

    # ── OpenFoodFacts ───────────────────────────
    OFF_USER_AGENT: str = "NutriLensAI/1.0"
    OFF_BASE_URL: str = "https://world.openfoodfacts.org/api/v0/product"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — loaded once at startup."""
    return Settings()


settings = get_settings()
