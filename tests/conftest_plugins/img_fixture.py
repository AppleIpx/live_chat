import io

import pytest
from fastapi import UploadFile
from PIL import Image


@pytest.fixture()
def fake_image() -> UploadFile:
    """The fixture that generates the image."""
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="png")
    image_bytes.seek(0)
    return UploadFile(
        filename="test_image.png",
        file=image_bytes,
    )
