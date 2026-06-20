from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    DATABASE_URL: str = Field(default="")
    RABBITMQ_URL: str = Field(default="")

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    DEMUCS_LOG_PATH: Path = BASE_DIR / "logs" / "demucs.log"

    TIMEZONE: str = "Europe/Bucharest"

    SESSION_COOKIE_NAME: str = "browser_session"
    SESSION_LIFETIME_DAYS: int = 30
    COOKIE_SECURE: bool = True

settings = Settings()
