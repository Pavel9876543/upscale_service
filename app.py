import os
import uuid
from io import BytesIO

import redis
from celery.result import AsyncResult
from flask import Flask, jsonify, request, send_file, url_for

from tasks import UPLOAD_TTL_SECONDS, celery, upscale_task


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))

storage = redis.from_url(REDIS_URL)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    @app.post("/upscale")
    def create_upscale_task():
        if "file" not in request.files:
            return jsonify({"error": "Field 'file' is required"}), 400

        uploaded_file = request.files["file"]

        if uploaded_file.filename == "":
            return jsonify({"error": "Filename is empty"}), 400

        image_bytes = uploaded_file.read()

        if not image_bytes:
            return jsonify({"error": "File is empty"}), 400

        upload_id = uuid.uuid4().hex
        storage.setex(f"upload:{upload_id}", UPLOAD_TTL_SECONDS, image_bytes)

        task = upscale_task.delay(upload_id)

        return jsonify({"task_id": task.id}), 202

    @app.get("/tasks/<task_id>")
    def get_task_status(task_id: str):
        task = AsyncResult(task_id, app=celery)

        response = {
            "task_id": task_id,
            "status": task.status,
        }

        if task.successful():
            filename = task.result
            response["file"] = filename
            response["url"] = url_for(
                "get_processed_file",
                file=filename,
                _external=True,
            )

        elif task.failed():
            response["error"] = str(task.result)

        return jsonify(response)

    @app.get("/processed/<path:file>")
    def get_processed_file(file: str):
        if "/" in file or "\\" in file:
            return jsonify({"error": "Invalid file name"}), 400

        processed_bytes = storage.get(f"processed:{file}")

        if processed_bytes is None:
            return jsonify({"error": "File not found or expired"}), 404

        return send_file(
            BytesIO(processed_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name=file,
        )

    return app


app = create_app()
