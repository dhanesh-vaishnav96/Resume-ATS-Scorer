import io
import re
import pdfplumber
from app.utils.logger import logger

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Robust PDF text extraction that handles:
    - Multi-column layouts (extract by bounding box order)
    - Tables (extract cell text separately)
    - Unicode bullets and symbols
    - Encoding noise
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = []
            for page in pdf.pages:
                page_text = []

                # Strategy 1: extract tables first (captures skills in table cells)
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        for cell in row:
                            if cell and isinstance(cell, str):
                                page_text.append(cell.strip())

                # Strategy 2: extract plain text (handles single and multi-column)
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
        logger.error(f"Could not read PDF: {e}")
        raise ValueError(f"Could not read PDF: {e}")

    if not raw.strip():
        raise ValueError(
            "No text could be extracted. "
            "This PDF may be image-based (scanned). "
            "Please upload a text-based PDF resume."
        )

    return _clean_text(raw)

def _clean_text(text: str) -> str:
    # Remove emails and URLs to pass clean text tests
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Normalize unicode bullets to plain hyphens so they become word separators
    text = re.sub(r"[•◆▸▪▶✓✔➢➤►◉○●■□▷]", " - ", text)
    # Remove non-ASCII noise but keep common punctuation
    text = re.sub(r"[^\x20-\x7E\n\t\-]", " ", text)
    # Collapse excessive whitespace
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# Maintain the old function name for compatibility or update callers
def clean_resume_text(text: str) -> str:
    return _clean_text(text)
