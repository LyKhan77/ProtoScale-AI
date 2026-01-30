"""Configuration for Flask application."""
import os
from pathlib import Path


class Config:
    """Base configuration."""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    STORAGE_DIR = BASE_DIR / "storage"
    UPLOAD_DIR = STORAGE_DIR / "uploads"
    JOBS_DIR = STORAGE_DIR / "jobs"
    EXPORT_DIR = STORAGE_DIR / "exports"

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6352/0")

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6352/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6352/0")

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Job settings
    JOB_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours

    # GPU settings
    GPU_DEVICE = os.getenv("GPU_DEVICE", "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu")

    # AI Model settings
    TRIPOSR_MODEL_ID = "stabilityai/TripoSR"

    # Mesh settings
    MIN_WALL_THICKNESS_MM = 1.2
    MESH_RESOLUTION = 256

    # ProtoScale-specific settings
    ENABLE_SCALING = True
    DEFAULT_SCALE = 1.0
    MIN_SCALE = 0.5
    MAX_SCALE = 5.0


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    REDIS_URL = "redis://localhost:6352/1"
    CELERY_BROKER_URL = "redis://localhost:6352/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6352/1"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
