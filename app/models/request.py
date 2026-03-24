from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    job_description: str = Field(..., min_length=10, description="Full job description text")
