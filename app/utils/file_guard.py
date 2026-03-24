from fastapi import HTTPException, UploadFile
from app.config import settings

def validate_file_type(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is supported.")

def validate_file_size(file: UploadFile):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=413, detail=f"File exceeds size limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")
