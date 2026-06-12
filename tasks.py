import os
import uuid

import redis
from celery import Celery

from upscale import upscale_bytes


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BROKER_URL = os.getenv("BROKER_URL", REDIS_URL)
RESULT_BACKEND = os.getenv("RESULT_BACKEND", REDIS_URL)

UPLOAD_TTL_SECONDS = int(os.getenv("UPLOAD_TTL_SECONDS", "3600"))
PROCESSED_TTL_SECONDS = int(os.getenv("PROCESSED_TTL_SECONDS", "86400"))

celery = Celery(
    "upscale_tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

storage = redis.from_url(REDIS_URL)


@celery.task(bind=True)
def upscale_task(self, upload_id: str) -> str:
    input_key = f"upload:{upload_id}"
    image_bytes = storage.get(input_key)

    if image_bytes is None:
        raise FileNotFoundError("Uploaded image expired or not found")

    processed_bytes = upscale_bytes(image_bytes)

    filename = f"{uuid.uuid4().hex}.png"
    output_key = f"processed:{filename}"

    storage.setex(output_key, PROCESSED_TTL_SECONDS, processed_bytes)
    storage.delete(input_key)

    return filename
