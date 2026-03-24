import google.generativeai as genai
import json
import asyncio
from app.config import settings
from app.utils.logger import logger

genai.configure(api_key=settings.GEMINI_API_KEY)

class AIEngine:
    def __init__(self):
        # gemini-1.5-flash is more stable and has higher RPM limits on Free Tier
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        # Semaphore ensure only ONE AI call happens at a time across the entire app
        # preventing concurrent hits that trigger 429 errors.
        self._semaphore = asyncio.Semaphore(1)

    def _build_prompt(self, ats_score, grade, matched, missing, skill_s, proj_s, edu_s, exp_s, soft_skills=None) -> str:
        soft_line = f"Soft Skills Detectied: {', '.join(soft_skills)}" if soft_skills else "Soft Skills: Not detected"
        return f"""You are a senior technical recruiter. Evaluate the following candidate summary:

ATS Score: {ats_score}/100 (Grade: {grade})
Matched Technical Skills: {', '.join(matched) if matched else 'None'}
Missing Technical Skills: {', '.join(missing) if missing else 'None'}
{soft_line}

Write a concise, professional 2-sentence hiring recommendation strictly explaining:
1. **Strong Area**: Where the candidate excels technically or interpersonally.
2. **Weak Area**: Where the candidate has gaps or needs improvement.

Do NOT state if they are "eligible" or "highly recommended". Focus strictly on Strengths and Weaknesses.
Be direct. Do not use bullet points. Do not start with "Based on the analysis". 
"""

    def _fallback_recommendation(self, score: float, grade: str, matched: list, missing: list) -> str:
        """A rule-based backup describing strengths and weaknesses."""
        strengths = f"Candidate excels in {', '.join(matched[:2])}" if matched else "Limited technical matches"
        weaknesses = f"There are gaps in {', '.join(missing[:3])}" if missing else "No major technical gaps detected"
        return f"{strengths}. {weaknesses}."

    async def generate_recommendation(self, resume_text: str, jd_text: str, scores: dict, matched_skills: list, missing_skills: list, soft_skills: list = None) -> str:
        """Generates a professional hiring recommendation with sequential processing and retry logic."""
        max_retries = 3
        ats_score = scores.get("total", 0)
        grade = scores.get("grade", "D")
        
        prompt = self._build_prompt(
            ats_score, grade, matched_skills, missing_skills,
            scores.get("skills", 0), scores.get("projects", 0),
            scores.get("education", 0), scores.get("experience", 0),
            soft_skills
        )
        
        async with self._semaphore:
            for attempt in range(max_retries):
                try:
                    # Run the synchronous generate_content in a thread pool to avoid blocking FastAPI
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
                    return response.text.strip()
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg and attempt < max_retries - 1:
                        # Successive backoff: 3s, 6s
                        wait = (attempt + 1) * 3
                        logger.warning(f"Gemini 429 triggered. Waiting {wait}s (Sequential Queue active).")
                        await asyncio.sleep(wait)
                    else:
                        logger.warning(f"Gemini failed after {attempt+1} attempts: {e}. Using fallback.")
                        return self._fallback_recommendation(ats_score, grade, matched_skills, missing_skills)

ai_engine = AIEngine()
