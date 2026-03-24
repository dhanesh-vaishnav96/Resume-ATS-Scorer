import re
from typing import Dict, List, Tuple
from app.utils.logger import logger

class ATSScorer:
    def __init__(self):
        self.weights = {
            "skills": 0.50,
            "projects": 0.30,
            "education": 0.10,
            "experience": 0.10
        }

    def calculate_skills_score(self, resume_skills: set, jd_skills: set) -> float:
        if not jd_skills: return 50.0
        matched = resume_skills.intersection(jd_skills)
        # Score = (Matched / Total) * 50. Normalize to avoid 0 if same base exists.
        score = (len(matched) / len(jd_skills)) * 50
        return min(50.0, score)

    def calculate_project_score(self, text: str, jd_skills: set) -> float:
        from app.core.matcher import matcher
        projects = matcher.extract_projects(text)
        if not projects: return 0.0
        if not jd_skills: return 30.0
            
        project_text = " ".join(projects).lower()
        skills_found = sum(1 for skill in jd_skills if re.search(rf'\b{re.escape(skill.lower())}\b', project_text))
        
        # Normalize: if we found at least 3 skills in projects, we consider it a strong proof.
        score = (skills_found / max(1, len(jd_skills))) * 60 # Boost project relevance
        return min(30.0, score)

    def calculate_education_score(self, text: str) -> float:
        text_lower = text.lower()
        cgpa_pattern = r'cgpa\s*[:\-]?\s*(\d+(\.\d+)?)'
        percent_pattern = r'(\d+(\.\d+)?)\s*%'
        
        masters_keywords = ["master", "m.tech", "mca", "mba", "m.sc"]
        bachelor_keywords = ["bachelor", "b.tech", "bca", "b.sc", "b.e"]
        
        scores = []
        for m in re.finditer(cgpa_pattern, text_lower):
            try:
                val = float(m.group(1))
                if val <= 10.0: scores.append(val)
                elif val <= 100.0: scores.append(val/10.0)
            except: continue
            
        for m in re.finditer(percent_pattern, text_lower):
            try:
                val = float(m.group(1))
                if val <= 100.0: scores.append(val/10.0)
            except: continue

        base_score = max(scores) if scores else 0.0
        
        # Industry Weighting: Masters (+1.0), Bachelors (+0.5)
        if any(kw in text_lower for kw in masters_keywords): base_score += 1.0
        elif any(kw in text_lower for kw in bachelor_keywords): base_score += 0.5
        
        return min(10.0, max(3.0, base_score))

    def calculate_experience_score(self, text: str) -> float:
        from app.core.matcher import matcher
        return matcher.extract_experience_score(text)

    def get_grade(self, score: float) -> str:
        if score >= 85: return "A (Highly Recommended)"
        if score >= 70: return "B+ (Strong Candidate)"
        if score >= 55: return "B (Consider)"
        if score >= 40: return "C (Potential)"
        return "D (Not Recommended)"

    def calculate_total_score(self, resume_text: str, jd_text: str, resume_skills: set, jd_skills: set) -> Tuple[float, Dict, float]:
        """Returns (total_score, sub_scores, confidence_score)."""
        s_score = self.calculate_skills_score(resume_skills, jd_skills)
        p_score = self.calculate_project_score(resume_text, jd_skills)
        e_score = self.calculate_education_score(resume_text)
        ex_score = self.calculate_experience_score(resume_text)
        
        total = s_score + p_score + e_score + ex_score
        sub_scores = {"skills": s_score, "projects": p_score, "education": e_score, "experience": ex_score}
        
        # Confidence score: based on skill density and text quality
        # If skills/length ratio is very low, confidence is lowered.
        text_len = len(resume_text.split())
        skill_density = len(resume_skills) / max(1, text_len)
        confidence = min(1.0, 0.5 + (skill_density * 5))
        
        return round(min(100.0, total), 2), sub_scores, round(confidence, 2)

scorer = ATSScorer()
