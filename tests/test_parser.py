from app.core.parser import clean_resume_text

def test_clean_resume_text():
    raw_text = "Contact: test@gmail.com, visit http://example.com. Hello World!"
    cleaned = clean_resume_text(raw_text)
    assert "test@gmail.com" not in cleaned
    assert "http://example.com" not in cleaned
    assert "Hello World!" in cleaned
