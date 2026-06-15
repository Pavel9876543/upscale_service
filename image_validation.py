from typing import Optional

from config import ALLOWED_IMAGE_TYPES, ALLOWED_IMAGE_TYPES_MESSAGE


TIFF_SIGNATURES = (
    b"II*\x00",  # classic TIFF, little endian
    b"MM\x00*",  # classic TIFF, big endian
    b"II+\x00",  # BigTIFF, little endian
    b"MM\x00+",  # BigTIFF, big endian
)


def detect_image_type(image_bytes: bytes) -> Optional[str]:
    """Detect a supported image type by its magic bytes."""
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "jpg"

    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if image_bytes.startswith(b"BM"):
        return "bmp"

    if image_bytes.startswith(TIFF_SIGNATURES):
        return "tiff"

    return None


def validate_allowed_image_type(image_bytes: bytes) -> str:
    """
    Return the detected image type or raise ValueError with a user-friendly error.

    Validation is based on file signatures rather than a filename extension or
    user-provided Content-Type header.
    """
    image_type = detect_image_type(image_bytes)

    if image_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Unsupported image type. "
            f"Allowed formats: {ALLOWED_IMAGE_TYPES_MESSAGE}."
        )

    return image_type
