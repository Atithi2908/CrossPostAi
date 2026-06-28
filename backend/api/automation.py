from fastapi import APIRouter, HTTPException, Depends, Header, Request
from models.user import User
from api.dependencies import get_current_user
from services.worker import run_single_cycle
from core.logger import setup_logger
from core.config import settings
from typing import Optional

logger = setup_logger("automation_api")
router = APIRouter()

async def verify_automation_auth(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Dependency that checks for EITHER a valid X-API-Key OR a valid logged-in user.
    """
    # 1. Check API Key
    if x_api_key and settings.AUTOMATION_API_KEY and x_api_key == settings.AUTOMATION_API_KEY:
        return {"auth_type": "api_key"}
        
    # 2. Check User Token (Fallback for Frontend "Sync Now" button)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from jose import jwt
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return {"auth_type": "user", "user_id": user_id}
        except Exception:
            pass
            
    raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key or Session Token")

@router.post("/sync")
def trigger_sync(auth_info: dict = Depends(verify_automation_auth)):
    """
    Triggers a manual automation cycle.
    Can be called by cron jobs (via X-API-Key) or the frontend (via JWT).
    """
    caller = f"User {auth_info.get('user_id')}" if auth_info.get("auth_type") == "user" else "Cron Scheduler"
    logger.info(f"Manual sync triggered by {caller}")
    
    try:
        summary = run_single_cycle()
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
