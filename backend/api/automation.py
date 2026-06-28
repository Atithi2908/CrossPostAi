from fastapi import APIRouter, HTTPException, Depends
from models.user import User
from api.dependencies import get_current_user
from services.worker import run_single_cycle
from core.logger import setup_logger

logger = setup_logger("automation_api")
router = APIRouter()

@router.post("/sync")
def trigger_sync(current_user: User = Depends(get_current_user)):
    """
    Triggers a manual automation cycle.
    """
    logger.info(f"Manual sync triggered by user {current_user.id}")
    try:
        summary = run_single_cycle()
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
