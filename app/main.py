from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import analyze
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import ResumeIQException
import os

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="KL Prarambh Resume ATS Scorer",
    version="1.1.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(ResumeIQException)
async def resumeiq_exception_handler(request: Request, exc: ResumeIQException):
    logger.error(f"Application error: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message, "code": exc.__class__.__name__}
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An internal server error occurred.", "code": "InternalServerError"}
    )

# API Routes
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])

# Serve Static Files (UI)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "Welcome to KL Prarambh Resume ATS Scorer API. UI not found in frontend/ directory."}

@app.get("/health", tags=["Health"])
async def health_check():
    import shutil
    tesseract_available = shutil.which("tesseract") is not None
    poppler_available = shutil.which("pdftoppm") is not None
    
    return {
        "status": "ok", 
        "version": "1.1.0",
        "dependencies": {
            "tesseract": "available" if tesseract_available else "missing",
            "poppler": "available" if poppler_available else "missing"
        }
    }

@app.on_event("startup")
async def startup_event():
    logger.info("KL Prarambh application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("KL Prarambh application shutting down...")
