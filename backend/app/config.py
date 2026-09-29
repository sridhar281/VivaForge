"""
Central configuration for VivaForge backend.

All secrets/config come from environment variables (.env locally, real
env vars in production). Nothing here is hard-coded — see .env.example
for the full list of variables this app expects.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "VivaForge"
    ENV: str = "development"  # development | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- Database ---
    DATABASE_URL: str  # e.g. postgresql+psycopg2://user:pass@localhost:5432/vivaforge

    # --- CORS ---
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # --- LLM provider ---
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # --- Vector store ---
    CHROMA_PERSIST_DIR: str = "./storage/chroma"

    # --- Media / storage ---
    UPLOAD_DIR: str = "./storage/uploads"
    ARTIFACT_DIR: str = "./storage/artifacts"
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_UPLOAD_EXTENSIONS: str = "mp4,mp3,wav,pdf,ppt,pptx"

    # --- Whisper ---
    WHISPER_MODEL_SIZE: str = "base"  # tiny|base|small|medium|large-v3
    WHISPER_DEVICE: str = "cpu"

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",") if ext.strip()}


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — import this everywhere instead of instantiating Settings() directly."""
    return Settings()
