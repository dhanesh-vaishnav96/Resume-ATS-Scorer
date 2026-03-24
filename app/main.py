from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.endpoints import analyze
from app.config import settings
from app.utils.logger import logger
import os

app = FastAPI(
    title="ResumeIQ — AI-Powered ATS Resume Analyzer",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"message": "Welcome to ResumeIQ API. UI not found in frontend/ directory."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    logger.info("ResumeIQ application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ResumeIQ application shutting down...")
