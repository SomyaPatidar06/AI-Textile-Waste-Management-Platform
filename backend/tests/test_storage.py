import io
from PIL import Image
import pytest
from fastapi import HTTPException
from app.services.storage import validate_and_save_image


def create_test_image_bytes(format="JPEG", size=(100, 100), color=(255, 0, 0)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_valid_jpeg_upload():
    img_bytes = create_test_image_bytes("JPEG")
    saved_path, secure_filename, sha256_hash = validate_and_save_image(img_bytes, "fabric.jpg")
    assert saved_path.endswith(secure_filename)
    assert len(sha256_hash) == 64
    assert secure_filename.endswith(".jpeg") or secure_filename.endswith(".jpg")


def test_valid_png_upload():
    img_bytes = create_test_image_bytes("PNG")
    saved_path, secure_filename, sha256_hash = validate_and_save_image(img_bytes, "swatch.png")
    assert secure_filename.endswith(".png")


def test_corrupt_image_rejected():
    corrupt_bytes = b"This is not a real image file, just random plaintext."
    with pytest.raises(HTTPException) as exc:
        validate_and_save_image(corrupt_bytes, "fake_image.jpg")
    assert exc.value.status_code in [400, 415]


def test_empty_file_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_and_save_image(b"", "empty.jpg")
    assert exc.value.status_code == 400


def test_oversized_file_rejected(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "MAX_FILE_SIZE_BYTES", 500)
    img_bytes = create_test_image_bytes("JPEG", size=(500, 500))
    with pytest.raises(HTTPException) as exc:
        validate_and_save_image(img_bytes, "huge.jpg")
    assert exc.value.status_code == 413
