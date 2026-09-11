import io
import os
import uuid

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_DIMENSION = 1600  # px, longest side after resize


def _ensure_upload_dir() -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    return settings.UPLOAD_DIR


async def validate_and_compress_screenshot(file: UploadFile) -> str:
    """Validates an uploaded image, compresses it with Pillow, saves it to disk,
    and returns the relative file path to store in the DB."""

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, or WEBP images are allowed.",
        )

    raw_bytes = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(raw_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.verify()
        # Re-open after verify() because verify() leaves the file unusable for further ops
        image = Image.open(io.BytesIO(raw_bytes))
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file.") from exc

    image = image.convert("RGB")
    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    upload_dir = _ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(upload_dir, filename)

    image.save(file_path, format="JPEG", quality=75, optimize=True)

    return file_path
