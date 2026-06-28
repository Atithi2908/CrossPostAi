from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import instagram, linkedin, pipeline, auth, automation
import traceback
import subprocess
from core.logger import setup_logger

logger = setup_logger("startup")

# Run ffmpeg diagnostics on startup
try:
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[0]
    codecs = subprocess.run(["ffmpeg", "-codecs"], capture_output=True, text=True).stdout
    formats = subprocess.run(["ffmpeg", "-formats"], capture_output=True, text=True).stdout
    logger.info(f"Startup Diagnostics - FFmpeg Version: {version}")
    logger.info(f"Startup Diagnostics - FFmpeg Codecs snippet:\n{codecs[:500]}...")
    logger.info(f"Startup Diagnostics - FFmpeg Formats snippet:\n{formats[:500]}...")
except Exception as e:
    logger.error(f"Failed to run FFmpeg startup diagnostics: {str(e)}")

app = FastAPI(title="PostMorph AI")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL,   "http://localhost:5173",
        "https://cross-post-ai.vercel.app",], # Allow frontend specifically and fallback to *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Centralized error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logger = logging.getLogger("error_handler")
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="", tags=["Users"]) # For /users/me
app.include_router(instagram.router, prefix="/instagram", tags=["Instagram"])
app.include_router(linkedin.router, prefix="/linkedin", tags=["LinkedIn"])
app.include_router(pipeline.router)
app.include_router(automation.router, prefix="/automation", tags=["Automation"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "PostMorph AI backend running"}
