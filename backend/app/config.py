import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "app" / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
OUTPUTS_DIR = STORAGE_DIR / "outputs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

CORS_ORIGINS = ["*"]  # Allow all origins during development

# GPU config
DEVICE = os.getenv("HUNYUAN_DEVICE", "cuda:0")
MODEL_PATH = os.getenv("HUNYUAN_MODEL_PATH", "tencent/Hunyuan3D-2")

# rembg model
REMBG_MODEL = os.getenv("REMBG_MODEL", "u2net")
