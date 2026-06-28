from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.logger import setup_logger
from services.instagram import InstagramService
from services.audio import AudioService
from services.transcript import TranscriptService
from services.rewrite import RewriteService
from services.publish import PublishService
from models.user import User
from api.dependencies import get_current_user
from core.database import get_db

logger = setup_logger("pipeline_api")
router = APIRouter()

instagram_service = InstagramService()
audio_service = AudioService()
transcript_service = TranscriptService()
rewrite_service = RewriteService()
publish_service = PublishService()

class PublishRequest(BaseModel):
    linkedin_post: str

@router.post("/generate")
def generate_post(current_user: User = Depends(get_current_user)):
    """
    Downloads latest reel, extracts audio, transcribes, and generates LinkedIn post.
    Does NOT publish.
    """
    logger.info(f"Starting /generate pipeline for user {current_user.id}")
    
    if not current_user.instagram_access_token or not current_user.instagram_account_id:
        raise HTTPException(status_code=400, detail="Instagram not connected")
        
    try:
        # 1. Download Reel
        video_path = instagram_service.download_reel(
            current_user.instagram_account_id, 
            current_user.instagram_access_token
        )
        
        # 2. Extract Audio
        audio_path = audio_service.extract_audio(video_path)
        
        # 3. Transcribe
        transcript_text = transcript_service.transcribe(audio_path)
            
            
        # 4. Rewrite for LinkedIn
        linkedin_post = rewrite_service.rewrite_for_linkedin(transcript_text)
        
        return {
            "success": True,
            "message": "Generated LinkedIn post successfully",
            "linkedin_post": linkedin_post
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
def publish_to_linkedin(request: PublishRequest, current_user: User = Depends(get_current_user)):
    """
    Publishes a provided text string to LinkedIn.
    """
    if not current_user.linkedin_access_token or not current_user.linkedin_author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")
        
    try:
        result = publish_service.publish_to_linkedin(
            request.linkedin_post,
            current_user.linkedin_access_token,
            current_user.linkedin_author_urn
        )
        return {
            "success": True,
            "message": "Published successfully",
            "post_id": result.get("id", ""),
            "published_at": result.get("created", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-and-publish")
def generate_and_publish(current_user: User = Depends(get_current_user)):
    """
    End-to-end pipeline: Reel -> Download -> Transcribe -> AI Rewrite -> Publish
    """
    # Verify connections first
    if not current_user.instagram_access_token or not current_user.instagram_account_id:
        raise HTTPException(status_code=400, detail="Instagram not connected")
    if not current_user.linkedin_access_token or not current_user.linkedin_author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    try:
        # Generate
        video_path = instagram_service.download_reel(
            current_user.instagram_account_id, 
            current_user.instagram_access_token
        )
        audio_path = audio_service.extract_audio(video_path)
        transcript_text = transcript_service.transcribe(audio_path)
            
        linkedin_post = rewrite_service.rewrite_for_linkedin(transcript_text)
        
        # Publish
        result = publish_service.publish_to_linkedin(
            linkedin_post,
            current_user.linkedin_access_token,
            current_user.linkedin_author_urn
        )
        
        return {
            "success": True,
            "message": "Successfully generated and published",
            "linkedin_post": linkedin_post,
            "post_id": result.get("id", "")
        }
        
    except Exception as e:
        logger.error(f"End-to-end pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
