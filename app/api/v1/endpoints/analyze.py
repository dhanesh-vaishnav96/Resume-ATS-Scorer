import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.models.response import AnalysisResponse, SubScores
from app.core.parser import extract_text_from_pdf, clean_resume_text
from app.core.matcher import matcher
from app.core.scorer import scorer
from app.core.ai_engine import ai_engine
from app.utils.file_guard import validate_file_type, validate_file_size
from app.utils.logger import logger
from app.config import settings

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    request_id = str(uuid.uuid4())
    logger.info(f"Received analysis request", extra={"request_id": request_id})
    
    # 1. Validation
    validate_file_type(resume)
    validate_file_size(resume)
    
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    
    # 2. Save file temporarily
    file_path = os.path.join(settings.UPLOADS_DIR, f"{request_id}_{resume.filename}")
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await resume.read())
    
    try:
        # 3. Extraction
        # Read file as bytes for the new robust parser
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            
        resume_text = extract_text_from_pdf(pdf_bytes)
        if not resume_text:
            raise HTTPException(status_code=500, detail="Failed to extract text from resume.")
            
        # 4. Rule-based Matching (100% locally from skills_db.json)
        jd_skills_set = matcher.get_combined_skills(job_description)
        resume_skills_set = matcher.get_combined_skills(resume_text)
        
        matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
        missing_skills = sorted(list(jd_skills_set - resume_skills_set))
        other_skills = sorted(list(resume_skills_set - jd_skills_set))
        
        # NEW: Soft Skill Extraction (Rule-based)
        from app.core.matcher import extract_soft_skills
        soft_skills = extract_soft_skills(resume_text)
        
        # 5. Scoring
        total_score, sub_scores_dict = scorer.calculate_total_score(
            resume_text, job_description, resume_skills_set, jd_skills_set
        )
        grade = scorer.get_grade(total_score)
        
        # Add total and grade to sub_scores for recommendation context
        recommendation_scores = {**sub_scores_dict, "total": total_score, "grade": grade}
        
        # 6. Recommendation (The ONLY Gemini call)
        recommendation = await ai_engine.generate_recommendation(
            resume_text, 
            job_description, 
            recommendation_scores,
            matched_skills,
            missing_skills,
            soft_skills=soft_skills
        )
        
        # 7. Cleanup (background task)
        background_tasks.add_task(os.remove, file_path)
        
        return AnalysisResponse(
            request_id=request_id,
            ats_score=round(total_score, 2),
            grade=grade,
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
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
