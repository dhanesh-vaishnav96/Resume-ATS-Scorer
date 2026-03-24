import pytest
from app.core.matcher import matcher, extract_skills_from_text, extract_soft_skills

def test_rule_based_match():
    text = "I am a Python developer experienced in FastAPI and Docker."
    matches = matcher.rule_based_match(text)
    assert "python" in matches
    assert "fastapi" in matches
    assert "docker" in matches

def test_aws_deduplication():
    # If both AWS and Amazon Web Services are present, only one should be returned
    text = "Experienced in AWS and Amazon Web Services."
    matches = extract_skills_from_text(text)
    # Both normalize to "amazon web services"
    assert "amazon web services" in matches
    # Ensure there's no other AWS variant in the final set
    assert len([m for m in matches if "aws" in m or "amazon web" in m]) == 1

def test_skill_aliases():
    # "React.js" should match canonical "react"
    text = "Experienced in React.js and Node js."
    matches = extract_skills_from_text(text)
    assert "react" in matches
    assert "nodejs" in matches
    assert "javascript" in matches # react.js contains js alias

def test_skill_normalization_hyphens():
    # "Problem-solving" and "Problem solving" should both match canonical "problem solving"
    text1 = "Expert in problem-solving."
    text2 = "Excellent problem solving skills."
    
    matches1 = extract_soft_skills(text1)
    matches2 = extract_soft_skills(text2)
    
    assert "problem solving" in matches1
    assert "problem solving" in matches2

def test_soft_skills():
    text = "A proactive leader with great communication and teamwork skills."
    soft = extract_soft_skills(text)
    assert "proactive" in soft
    assert "leader" in soft
    assert "communication" in soft
    assert "teamwork" in soft
