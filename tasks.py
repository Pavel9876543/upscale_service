import uuid

import redis
from celery import Celery

from config import (
    BROKER_URL,
    PROCESSED_TTL_SECONDS,
    REDIS_URL,
    RESULT_BACKEND,
)
from upscale import upscale_bytes

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
