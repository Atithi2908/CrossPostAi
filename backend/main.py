from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import instagram, linkedin, pipeline, auth, automation
import traceback

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
