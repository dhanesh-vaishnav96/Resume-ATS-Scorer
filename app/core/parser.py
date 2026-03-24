import io
import re
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from app.utils.logger import logger
from app.utils.exceptions import ExtractionError

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Robust PDF text extraction with OCR fallback for scanned documents.
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = []
            for page in pdf.pages:
                page_text = []

                # Strategy 1: extract tables first
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        for cell in row:
                            if cell and isinstance(cell, str):
                                page_text.append(cell.strip())

                # Strategy 2: extract plain text
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text:
                    page_text.append(text)

                # Strategy 3: if still empty, try word-level extraction
                if not any(page_text):
                    words = page.extract_words()
                    if words:
                        page_text.append(" ".join(w["text"] for w in words))

                all_text.append("\n".join(page_text))

            raw = "\n".join(all_text)

    except Exception as e:
        logger.error(f"Could not read PDF structure: {e}")
        raw = ""

    # Check if we got substantive text. If < 100 chars, it's likely scanned or image-based.
    if len(raw.strip()) < 100:
        logger.info("Text extraction yielded minimal results. Attempting OCR fallback...")
        try:
            images = convert_from_bytes(pdf_bytes)
            ocr_text = []
            for img in images:
                text = pytesseract.image_to_string(img)
                ocr_text.append(text)
            raw = "\n".join(ocr_text)
            logger.info("OCR extraction completed successfully.")
        except Exception as ocr_err:
            logger.error(f"OCR fallback failed: {ocr_err}")
            raise ExtractionError(
                f"OCR fallback failed: {str(ocr_err)}. "
                "Ensure 'Tesseract-OCR' and 'Poppler' (pdftoppm) are installed and added to your system PATH."
            )

    if not raw.strip():
        raise ExtractionError("Extracted text is empty. Please upload a valid PDF resume.")

    return _clean_text(raw)

def _clean_text(text: str) -> str:
    # Remove emails and URLs
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Normalize unicode bullets
    text = re.sub(r"[•◆▸▪▶✓✔➢➤►◉○●■□▷]", " - ", text)
    # Remove non-ASCII noise but keep common punctuation
    text = re.sub(r"[^\x20-\x7E\n\t\-]", " ", text)
    # Collapse excessive whitespace
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def clean_resume_text(text: str) -> str:
    return _clean_text(text)
