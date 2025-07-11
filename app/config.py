from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    TIBCO_URL: str
    PYTHON_URL: str
    DB_PATH: Path = Path("comparisons.db")
    CACHE_SIZE: int = 100

    API_BASE_URL: str  # ← required for FastAPI endpoints
    DASHBOARD_URL: str = "http://localhost:8501"  # ← Streamlit URL (can override via .env)

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_RELOAD: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
