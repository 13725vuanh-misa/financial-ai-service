import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]

# Thông tin service
APP_NAME = "Financial AI Service"
APP_VERSION = "0.1.0"

# Thư mục lưu dữ liệu đầu ra
STORAGE_DIR = BASE_DIR / "storage"
DATASETS_DIR = STORAGE_DIR / "datasets"
MODELS_DIR = STORAGE_DIR / "models"
REPORTS_DIR = STORAGE_DIR / "reports"

class Settings(BaseSettings):
    app_name: str = "Financial AI Service"
    app_version: str = "0.1.0"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
settings = Settings()