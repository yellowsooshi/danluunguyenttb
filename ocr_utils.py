"""Utility functions for performing OCR on uploaded label images.

This module handles text extraction from label images using Tesseract OCR.
Tesseract must be installed separately on the host system.
"""

from __future__ import annotations

import io
from typing import Union

from PIL import Image

try:
    import pytesseract  # type: ignore
except ImportError:  # pragma: no cover
    pytesseract = None


def extract_text(image_data: Union[bytes, io.BytesIO]) -> str:
    """Extract raw text from an image using Tesseract OCR.

    Parameters
    ----------
    image_data : Union[bytes, io.BytesIO]
        Raw bytes of the image or a BytesIO stream
        Supported formats: PNG, JPEG

    Returns
    -------
    str
        Extracted text content from the image (unprocessed)

    Raises
    ------
    RuntimeError
        If Tesseract engine is unavailable or fails to run
    """
    # Convert bytes to BytesIO if needed
    if isinstance(image_data, bytes):
        byte_stream = io.BytesIO(image_data)
    else:
        byte_stream = image_data
    
    # Open image with Pillow
    try:
        image = Image.open(byte_stream)
    except Exception as exc:
        raise RuntimeError(f"Failed to open image for OCR: {exc}")

    if pytesseract is None:
        raise RuntimeError(
            "pytesseract is not installed or Tesseract engine is unavailable. "
            "Install pytesseract and tesseract-ocr on your system to enable OCR."
        )

    # Perform OCR with Tesseract
    try:
        text = pytesseract.image_to_string(image, lang="eng")
    except Exception as exc:
        raise RuntimeError(f"Tesseract OCR failed: {exc}")
    
    return text
