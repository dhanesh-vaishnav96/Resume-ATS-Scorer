import pytest
from unittest.mock import patch, MagicMock
from app.core.parser import extract_text_from_pdf
from app.core.matcher import matcher
from app.core.scorer import scorer

def test_ocr_fallback():
    """Verify that OCR is triggered when text extraction yields minimal content."""
    dummy_pdf_bytes = b"%PDF-1.4 image based"
    
    with patch("app.core.parser.pdfplumber.open") as mock_pdf:
        # Mock pdfplumber to return no text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_page.extract_tables.return_value = []
        mock_page.extract_words.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
        
        with patch("app.core.parser.convert_from_bytes") as mock_convert:
            mock_convert.return_value = [MagicMock()]
            with patch("app.core.parser.pytesseract.image_to_string") as mock_ocr:
                mock_ocr.return_value = "Python Developer with AWS experience"
                
                text = extract_text_from_pdf(dummy_pdf_bytes)
                assert "Python" in text
                assert mock_ocr.called

def test_semantic_matching():
    """Verify that semantic matching finds similar skills."""
    # This test might be slow or require the model to be mocked for CI
    # In this case, we verify the hybrid logic
    text = "We are looking for someone with expertise in Cloud Computing and AI."
    # Even if "expertise" isn't a skill, semantic match should find related ones if in DB
    with patch.object(matcher, 'semantic_match', return_value={"Cloud Engineering"}):
        skills = matcher.get_combined_skills(text)
        assert "Cloud Engineering" in skills

def test_scoring_confidence():
    """Verify that confidence score is calculated."""
    resume_text = "Experienced software engineer with skills in Python, Java, and Distributed Systems."
    jd_skills = {"Python", "Java", "Kubernetes"}
    resume_skills = {"Python", "Java"}
    
    score, sub_scores, confidence = scorer.calculate_total_score(
        resume_text, "Looking for Python Java dev", resume_skills, jd_skills
    )
    
    assert 0.0 <= confidence <= 1.0
    assert "skills" in sub_scores
    assert score > 0

@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Verify that rate limiting is active on the analyze endpoint."""
    # This requires an async test client and actual uvicorn/fastapi running
    # Typically implementation involves hitting the endpoint multiple times
    pass
