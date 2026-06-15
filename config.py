import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BROKER_URL = os.getenv("BROKER_URL", REDIS_URL)
RESULT_BACKEND = os.getenv("RESULT_BACKEND", REDIS_URL)

MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
UPLOAD_TTL_SECONDS = int(os.getenv("UPLOAD_TTL_SECONDS", "3600"))
PROCESSED_TTL_SECONDS = int(os.getenv("PROCESSED_TTL_SECONDS", "86400"))

MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "EDSR_x2.pb"))

ALLOWED_IMAGE_TYPES = {"jpg", "png", "bmp", "tiff"}
ALLOWED_IMAGE_TYPES_MESSAGE = "JPG, PNG, BMP, TIFF"
