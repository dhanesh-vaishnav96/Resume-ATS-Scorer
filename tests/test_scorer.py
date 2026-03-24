from app.core.scorer import scorer

def test_calculate_education_score_masters_multiline():
    # Priority: Master's should be taken over Bachelor's even if on different lines
    text = "Degree: Masters in Data Science\nCGPA: 9.3\nBachelors: 7.0 CGPA"
    score = scorer.calculate_education_score(text)
    assert score == 9.3

def test_calculate_education_score_bachelors_percent():
    # Percentage should be converted to 10-point scale
    text = "B.Tech in CS: 88% marks"
    score = scorer.calculate_education_score(text)
    assert score == 8.8

def test_calculate_education_score_hyphen_separator():
    # Handle "CGPA - 8.5"
    text = "University: SPSU\nCGPA - 8.5"
    score = scorer.calculate_education_score(text)
    assert score == 8.5

def test_calculate_experience_score_fresher():
    # New rule: Freshers get 0.0
    text = "I am a fresher with no previous job experience."
    score = scorer.calculate_experience_score(text)
    assert score == 0.0

def test_calculate_experience_score_internship():
    # Internship counts as experience (min 4.0)
    text = "Completed Internship at Tech Corp"
    score = scorer.calculate_experience_score(text)
    assert score >= 4.0

def test_calculate_experience_score_explicit():
    text = "Work Experience: 4 years as a lead engineer."
    score = scorer.calculate_experience_score(text)
    assert score == 10.0
