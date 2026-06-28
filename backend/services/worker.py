import asyncio
import os
from core.logger import setup_logger
from core.database import SessionLocal
from models.user import User
from services.instagram import InstagramService
from services.audio import AudioService
from services.transcript import TranscriptService
from services.rewrite import RewriteService
from services.publish import PublishService

logger = setup_logger("automation_worker")

instagram_service = InstagramService()
audio_service = AudioService()
transcript_service = TranscriptService()
rewrite_service = RewriteService()
publish_service = PublishService()

def process_user(user: User, db) -> dict:
    result = {"user_id": str(user.id), "status": "skipped", "error": None}
    try:
        # Fetch latest reel
        latest_reel = instagram_service.get_latest_reel(user.instagram_account_id, user.instagram_access_token)
        reel_id = latest_reel.get("id")
        
        if not reel_id:
            result["status"] = "error"
            result["error"] = "No reel ID found"
            return result
            
        if reel_id == user.last_processed_reel_id:
            logger.info(f"User {user.id}: No new reel detected (Reel ID: {reel_id})")
            return result
            
        logger.info(f"User {user.id}: New reel detected! (Reel ID: {reel_id})")
        
        # Download Reel
        video_path = instagram_service.download_reel(user.instagram_account_id, user.instagram_access_token)
        
        # Extract Audio
        audio_path = audio_service.extract_audio(video_path)
        
        # Transcribe
        transcript_text = transcript_service.transcribe(audio_path)
        
        # Rewrite for LinkedIn
        linkedin_post = rewrite_service.rewrite_for_linkedin(transcript_text)
        logger.info(f"User {user.id}: Post generated successfully.")
        
        # Publish to LinkedIn
        publish_result = publish_service.publish_to_linkedin(
            linkedin_post,
            user.linkedin_access_token,
            user.linkedin_author_urn
        )
        logger.info(f"User {user.id}: Post published to LinkedIn successfully.")
        
        # Update Database
        user.last_processed_reel_id = reel_id
        db.commit()
        
        result["status"] = "published"
        
    except Exception as e:
        logger.error(f"Error processing user {user.id}: {str(e)}")
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

def run_single_cycle() -> dict:
    logger.info("Starting automation cycle...")
    db = SessionLocal()
    summary = {
        "users_checked": 0,
        "new_reels_found": 0,
        "posts_published": 0,
        "errors": []
    }
    try:
        users = db.query(User).filter(
            User.instagram_account_id.isnot(None),
            User.instagram_access_token.isnot(None),
            User.linkedin_author_urn.isnot(None),
            User.linkedin_access_token.isnot(None)
        ).all()
        
        summary["users_checked"] = len(users)
        
        for user in users:
            res = process_user(user, db)
            if res["status"] == "published":
                summary["new_reels_found"] += 1
                summary["posts_published"] += 1
            elif res["status"] == "error":
                summary["errors"].append({"user_id": res["user_id"], "error": res["error"]})
                
    finally:
        db.close()
        
    logger.info(f"Automation cycle completed. Summary: {summary}")
    return summary

async def start_worker():
    logger.info("Background automation worker started.")
    try:
        while True:
            # Run in a separate thread so it doesn't block the async event loop
            await asyncio.to_thread(run_single_cycle)
            
            logger.info("Worker sleeping for 15 minutes...")
            await asyncio.sleep(15 * 60)
            
    except asyncio.CancelledError:
        logger.info("Background automation worker stopped gracefully.")
