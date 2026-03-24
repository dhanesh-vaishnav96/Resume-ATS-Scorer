import uuid
import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, Request, BackgroundTasks
from app.models.response import AnalysisResponse, SubScores
from app.core.parser import extract_text_from_pdf
from app.core.matcher import matcher
from app.core.scorer import scorer
from app.core.ai_engine import ai_engine
from app.utils.file_guard import validate_file_type, validate_file_size
from app.utils.logger import logger
from app.utils.exceptions import ExtractionError, ValidationError, ResumeIQException
from app.config import settings

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Apply rate limiting manually if using helper or use decorator if configured in main
    # For this implementation, we rely on the limiter initialized in main.py
    # but we can also use the @limiter.limit("5/minute") if we import limiter here.
    from app.main import limiter
    
    request_id = str(uuid.uuid4())
    logger.info("Received analysis request", extra={"request_id": request_id})
    
    # 1. Validation
    try:
        validate_file_type(resume)
        validate_file_size(resume)
    except Exception as e:
        raise ValidationError(str(e))
    
    jd_clean = job_description.strip()
    if not jd_clean:
        raise ValidationError("Job description cannot be empty.")
    
    # 2. Save file temporarily (Async)
    file_path = os.path.join(settings.UPLOADS_DIR, f"{request_id}_{resume.filename}")
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await resume.read()
            await buffer.write(content)
        
        # 3. Extraction
        # Read file as bytes for the robust parser
        async with aiofiles.open(file_path, "rb") as f:
            pdf_bytes = await f.read()
            
        resume_text = extract_text_from_pdf(pdf_bytes)
        if not resume_text:
            raise ExtractionError("Failed to extract meaningful text from resume.")
            
        # 4. Matching (With Caching for JD skills)
        from app.utils.cache import cache_manager
        
        jd_skills_set = await cache_manager.get_jd_skills(jd_clean)
        if not jd_skills_set:
            jd_skills_set = matcher.get_combined_skills(jd_clean)
            await cache_manager.set_jd_skills(jd_clean, jd_skills_set)
        
        resume_skills_set = matcher.get_combined_skills(resume_text)
        
        matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
        missing_skills = sorted(list(jd_skills_set - resume_skills_set))
        other_skills = sorted(list(resume_skills_set - jd_skills_set))
        
        # Soft Skill Extraction
        soft_skills = matcher.extract_soft_skills(resume_text)
        
        # 5. Scoring
        total_score, sub_scores_dict, confidence_score = scorer.calculate_total_score(
            resume_text, jd_clean, resume_skills_set, jd_skills_set
        )
        grade = scorer.get_grade(total_score)
        
        # 6. Recommendation
        recommendation_scores = {**sub_scores_dict, "total": total_score, "grade": grade}
        recommendation = await ai_engine.generate_recommendation(
            resume_text, 
            jd_clean, 
            recommendation_scores,
            matched_skills,
            missing_skills,
            soft_skills=soft_skills
        )
        
        # 7. Cleanup
        background_tasks.add_task(os.remove, file_path)
        
        return AnalysisResponse(
            request_id=request_id,
            ats_score=total_score,
            grade=grade,
            confidence_score=confidence_score,
            resume_skills=list(resume_skills_set),
            skills_matched=matched_skills,
            skills_missing=missing_skills,
            skills_other=other_skills,
            soft_skills=soft_skills,
            sub_scores=SubScores(**sub_scores_dict),
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", extra={"request_id": request_id})
        if os.path.exists(file_path):
            os.remove(file_path)
        # Re-raise as ResumeIQException if not already one
        if isinstance(e, ResumeIQException):
            raise e
        raise ResumeIQException(f"Internal Processing Error: {str(e)}")
