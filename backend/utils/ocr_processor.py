"""
OCR Processor for bill scanning
"""
import io
import os
import shutil
import logging
from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

logger = logging.getLogger(__name__)


def get_tesseract_path() -> Optional[str]:
    """Find tesseract executable location."""
    for path in [
        shutil.which("tesseract"),
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/usr/bin/tesseract",
        "/opt/anaconda3/bin/tesseract",
    ]:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None


def ocr_from_image_bytes(image_bytes: bytes, tesseract_cmd: Optional[str] = None) -> Tuple[str, float]:
    """
    Perform OCR on image bytes

    Args:
        image_bytes: Raw image bytes
        tesseract_cmd: Path to tesseract executable (optional)

    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    cmd = tesseract_cmd or get_tesseract_path()
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    else:
        logger.warning("Tesseract executable not found in PATH or standard locations.")

    try:
        # Open image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Preprocess image
        processed_img = preprocess_image(image)

        # Perform OCR
        text = pytesseract.image_to_string(processed_img, config='--psm 6')
        if not text.strip():
            # Fallback to default PSM
            text = pytesseract.image_to_string(image)

        # Get confidence
        try:
            data = pytesseract.image_to_data(
                processed_img, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if str(conf) != '-1']
            avg_confidence = (sum(confidences) / len(confidences)) if confidences else 0.0
        except Exception:
            avg_confidence = 85.0 if text.strip() else 0.0

        return text, avg_confidence

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return "", 0.0


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR

    Args:
        image: PIL Image

    Returns:
        Preprocessed PIL Image
    """
    # Convert to grayscale
    gray = image.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)

    # Sharpness
    sharpener = ImageEnhance.Sharpness(gray)
    gray = sharpener.enhance(1.5)

    return gray

