from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SubScores(BaseModel):
    skills: float
    projects: float
    education: float
    experience: float

class AnalysisResponse(BaseModel):
    request_id: str
    ats_score: float
    grade: str
    confidence_score: float
    resume_skills: List[str]
    skills_matched: List[str]
    skills_missing: List[str]
    skills_other: List[str]
    soft_skills: List[str]
    sub_scores: SubScores
    recommendation: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)
