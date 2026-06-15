from threading import Lock

import cv2
import numpy as np

from config import MODEL_PATH

_scaler = None
_scaler_lock = Lock()


def get_scaler():
    """
    The model is loaded only once per Celery worker process.
    If Celery runs with several worker processes, each process will load its own copy.
    """
    global _scaler

    if _scaler is None:
        with _scaler_lock:
            if _scaler is None:
                if not MODEL_PATH.exists():
                    raise FileNotFoundError(
                        f"Model file not found: {MODEL_PATH}. "
                        "Run scripts/download_model.sh or place EDSR_x2.pb in the project root."
                    )
                if not hasattr(cv2, "dnn_superres"):
                    raise RuntimeError(
                        "OpenCV dnn_superres module is not available. "
                        "Install opencv-contrib-python-headless."
                    )

                scaler = cv2.dnn_superres.DnnSuperResImpl_create()
                scaler.readModel(str(MODEL_PATH))
                scaler.setModel("edsr", 2)
                _scaler = scaler

    return _scaler


def upscale_bytes(image_bytes: bytes) -> bytes:
    """
    Accepts an image as bytes and returns an upscaled PNG as bytes.
    Input and output image files are not saved to disk.
    """
    np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image file")

    result = get_scaler().upsample(image)

    ok, encoded = cv2.imencode(".png", result)
    if not ok:
        raise ValueError("Could not encode processed image")

    return encoded.tobytes()
