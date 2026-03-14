"""OCR and text extraction from PDFs and images."""

import io
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image
from PyPDF2 import PdfReader

# Optional: for PDFs without embedded text, convert to images then OCR
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from PDF. Uses PyPDF2 first; if empty, uses pdf2image + tesseract if available."""
    reader = PdfReader(str(path))
    text_parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text_parts.append(t)
    text = "\n".join(text_parts).strip()
    if text or not HAS_PDF2IMAGE:
        return text or ""
    # Fallback: render PDF to images and OCR
    images = convert_from_path(str(path))
    for img in images:
        text_parts.append(pytesseract.image_to_string(img))
    return "\n".join(text_parts).strip()


def extract_text_from_image(path: Path) -> str:
    """Extract text from image using Tesseract OCR."""
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return pytesseract.image_to_string(img).strip()


def extract_text_from_file(file_path: Path, content_type: Optional[str] = None) -> str:
    """Dispatch by extension or content type. Returns raw OCR/text."""
    path = Path(file_path)
    suffix = (path.suffix or "").lower()
    if suffix == ".pdf" or (content_type and "pdf" in content_type):
        return extract_text_from_pdf(path)
    if suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp") or (
        content_type and "image" in content_type
    ):
        return extract_text_from_image(path)
    # Default: try as image then PDF
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    try:
        return extract_text_from_image(path)
    except Exception:
        return ""
