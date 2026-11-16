import os
import hashlib
import uuid
import io
import re
from typing import Tuple
from PIL import Image
from fastapi import HTTPException, status
from app.core.config import settings


def _verify_magic_bytes(data: bytes) -> str:
    """Verifies image header magic bytes to prevent MIME spoofing attacks."""
    if len(data) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too small to be a valid image."
        )

    # JPEG: FF D8 FF
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"

    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    # WebP: 'RIFF' .... 'WEBP'
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Invalid image magic header. Allowed formats: JPEG, PNG, WEBP."
    )


def validate_and_save_image(file_bytes: bytes, filename: str) -> Tuple[str, str, str]:
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        max_mb = settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {max_mb} MB."
        )

    # 1. Magic bytes sniffing
    magic_format = _verify_magic_bytes(file_bytes)

    # 2. Pillow structural decode check
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
            img_format = (img.format or "").lower()
            if img_format not in ["jpeg", "jpg", "png", "webp"]:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported image format: {img_format}. Allowed formats: JPEG, PNG, WEBP."
                )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupt or invalid image content: {str(e)}"
        )

    sha256_hash = hashlib.sha256(file_bytes).hexdigest()

    # 3. Path traversal protection & filename sanitization
    clean_orig_name = os.path.basename(filename)
    clean_orig_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean_orig_name)
    ext = os.path.splitext(clean_orig_name)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = f".{magic_format}" if magic_format else ".jpg"

    secure_filename = f"{uuid.uuid4().hex}_{sha256_hash[:12]}{ext}"
    abs_upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(abs_upload_dir, exist_ok=True)
    destination_path = os.path.join(abs_upload_dir, secure_filename)

    # Verify canonical path remains strictly within upload directory
    abs_destination = os.path.abspath(destination_path)
    if os.path.commonpath([abs_destination, abs_upload_dir]) != abs_upload_dir:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Illegal file path traversal detected."
        )

    with open(abs_destination, "wb") as f:
        f.write(file_bytes)

    return destination_path, secure_filename, sha256_hash
