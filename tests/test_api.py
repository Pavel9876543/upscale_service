import io

import app as app_module
import tasks as tasks_module


class FakeStorage:
    def __init__(self):
        self.data = {}

    def setex(self, key, ttl, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.data.pop(key, None)


def test_post_upscale_returns_task_id(monkeypatch):
    fake_storage = FakeStorage()

    monkeypatch.setattr(app_module, "storage", fake_storage)
    monkeypatch.setattr(tasks_module, "storage", fake_storage)
    monkeypatch.setattr(tasks_module, "upscale_bytes", lambda image: b"processed-image")

    tasks_module.celery.conf.update(
        task_always_eager=True,
        task_store_eager_result=False,
    )

    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()

    response = client.post(
        "/upscale",
        data={"file": (io.BytesIO(b"source-image"), "lama_300px.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 202
    assert "task_id" in response.get_json()


def test_processed_file_returns_bytes(monkeypatch):
    fake_storage = FakeStorage()
    fake_storage.setex("processed:test.png", 3600, b"processed-image")

    monkeypatch.setattr(app_module, "storage", fake_storage)

    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()

    response = client.get("/processed/test.png")

    assert response.status_code == 200
    assert response.data == b"processed-image"
    assert response.content_type == "image/png"


def test_task_status_success(monkeypatch):
    class FakeResult:
        status = "SUCCESS"
        result = "result.png"

        def successful(self):
            return True

        def failed(self):
            return False

    monkeypatch.setattr(
        app_module,
        "AsyncResult",
        lambda task_id, app=None: FakeResult(),
    )

    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()

    response = client.get("/tasks/some-task-id")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "SUCCESS"
    assert data["file"] == "result.png"
    assert data["url"].endswith("/processed/result.png")


def test_post_upscale_without_file_returns_400():
    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()

    response = client.post("/upscale")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Field 'file' is required"
