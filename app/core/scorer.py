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
        """Skills Score = (Matched Skills / Total JD Skills) * 50"""
        if not jd_skills:
            return 50.0  # Avoid division by zero
        matched = resume_skills.intersection(jd_skills)
        score = (len(matched) / len(jd_skills)) * 50
        return min(50.0, score)

    def calculate_project_score(self, text: str, jd_skills: set) -> float:
        """Project Score = (Skills in projects / Total JD Skills) * 30"""
        from app.core.matcher import extract_projects
        projects = extract_projects(text)
        if not projects:
            return 0.0
            
        project_text = " ".join(projects).lower()
        # Count how many of the JD skills appear in the detected project sections
        skills_found = sum(1 for skill in jd_skills if re.search(rf'\b{re.escape(skill.lower())}\b', project_text))
        
        if not jd_skills:
            return 30.0
            
        score = (skills_found / len(jd_skills)) * 30
        return min(30.0, score)

    def calculate_education_score(self, text: str) -> float:
        """
        Education score based on CGPA/Percentage extraction.
        Linear scoring: CGPA 9.2 -> 9.2 pts, 85% -> 8.5 pts.
        Priority: Master's context > Bachelor's context > Highest Value.
        """
        text_lower = text.lower()
        
        # Patterns for CGPA (e.g., 9.2, 8.5) and Percentage (e.g., 85%)
        # Handles "CGPA: 8.5", "CGPA - 8.5", "CGPA 8.5"
        cgpa_pattern = r'cgpa\s*[:\-]?\s*(\d+(\.\d+)?)'
        percent_pattern = r'(\d+(\.\d+)?)\s*%'
        
        # Degree keywords for priority
        masters_keywords = ["master", "m.tech", "m.e", "m.sc", "mba", "mca", "postgraduate", "pg"]
        bachelor_keywords = ["bachelor", "b.tech", "b.e", "b.sc", "b.a", "b.com", "bca", "undergraduate", "ug"]
        
        matches = []  # List of (score out of 10, priority level)
        
        def get_priority(pos):
            # Check context (±100 characters) for degree keywords
            context = text_lower[max(0, pos-100):min(len(text_lower), pos+100)]
            if any(kw in context for kw in masters_keywords): return 3
            if any(kw in context for kw in bachelor_keywords): return 2
            return 1

        # 1. Search for CGPA matches
        for m in re.finditer(cgpa_pattern, text_lower):
            try:
                val = float(m.group(1))
                if val <= 10.0:
                    matches.append((val, get_priority(m.start())))
            except ValueError:
                continue
        
        # 2. Search for Percentage matches
        for m in re.finditer(percent_pattern, text_lower):
            try:
                val = float(m.group(1))
                if val <= 100.0:
                    # Normalize % to 10-point scale (e.g., 85% -> 8.5)
                    matches.append((val / 10.0, get_priority(m.start())))
            except ValueError:
                continue

        if matches:
            # Sort by priority (highest first), then by score (highest first)
            matches.sort(key=lambda x: (x[1], x[0]), reverse=True)
            return min(10.0, matches[0][0])
            
        # 3. Fallback based on degree keywords if no numeric score found
        if any(kw in text_lower for kw in masters_keywords): 
            return 7.0  # Master's mention but no CGPA
        if any(kw in text_lower for kw in bachelor_keywords): 
            return 5.0  # Bachelor's mention but no CGPA
            
        return 3.0  # Minimal score if nothing found

    def calculate_experience_score(self, text: str) -> float:
        """Experience score based on years of industry exposure (now from matcher)."""
        from app.core.matcher import extract_experience_score
        return extract_experience_score(text)

    def get_grade(self, score: float) -> str:
        if score >= 85: return "A"
        if score >= 70: return "B+"
        if score >= 55: return "B"
        if score >= 40: return "C"
        return "D"

    def calculate_total_score(self, resume_text: str, jd_text: str, resume_skills: set, jd_skills: set) -> Tuple[float, Dict]:
        skills_score = self.calculate_skills_score(resume_skills, jd_skills)
        project_score = self.calculate_project_score(resume_text, jd_skills)
        education_score = self.calculate_education_score(resume_text)
        experience_score = self.calculate_experience_score(resume_text)
        
        total = skills_score + project_score + education_score + experience_score
        sub_scores = {
            "skills": skills_score,
            "projects": project_score,
            "education": education_score,
            "experience": experience_score
        }
        return min(100.0, total), sub_scores

scorer = ATSScorer()
