from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "PostMorph AI"
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORAGE_DIR: str = os.path.join(BASE_DIR, "storage")
    TOKENS_DIR: str = os.path.join(STORAGE_DIR, "tokens")
    CACHE_DIR: str = os.path.join(STORAGE_DIR, "cache")
    OUTPUT_DIR: str = os.path.join(STORAGE_DIR, "output")
    LOGS_DIR: str = os.path.join(STORAGE_DIR, "logs")
    
    # Database and JWT
    DATABASE_URL: str | None = None
    JWT_SECRET_KEY: str | None = "super-secret-default-key-please-change"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080 # 7 days
    FRONTEND_URL: str = "http://localhost:5173"
    
    # API Keys
    # AI APIs
    DEEPGRAM_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    INSTAGRAM_CLIENT_ID: str | None = None
    INSTAGRAM_CLIENT_SECRET: str | None = None
    INSTAGRAM_REDIRECT_URI: str | None = None

    LINKEDIN_CLIENT_ID: str | None = None
    LINKEDIN_CLIENT_SECRET: str | None = None
    LINKEDIN_REDIRECT_URI: str | None = None
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
for d in [settings.TOKENS_DIR, settings.CACHE_DIR, settings.OUTPUT_DIR, settings.LOGS_DIR]:
    os.makedirs(d, exist_ok=True)
