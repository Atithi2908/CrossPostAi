from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from services.linkedin import LinkedInService
from core.database import get_db
from models.user import User
from api.dependencies import get_current_user
from core.security import create_oauth_state, decode_oauth_state
from core.config import settings

router = APIRouter()
service = LinkedInService()

@router.get("/login")
def login(current_user: User = Depends(get_current_user)):
    try:
        state = create_oauth_state(str(current_user.id))
        url = service.get_login_url(state)
        return {"login_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def callback(code: str, state: str, db: Session = Depends(get_db)):
    error_url = f"{settings.FRONTEND_URL}/dashboard?provider=linkedin&success=false"
    success_url = f"{settings.FRONTEND_URL}/dashboard?provider=linkedin&success=true"

    user_id = decode_oauth_state(state)
    if not user_id:
        return RedirectResponse(url=error_url)
        
    import uuid
    try:
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
    except ValueError:
        return RedirectResponse(url=error_url)
        
    if not user:
        return RedirectResponse(url=error_url)
        
    try:
        token_data = service.handle_callback(code)
        
        # Save to database
        user.linkedin_access_token = token_data.get("access_token")
        user.linkedin_author_urn = token_data.get("author_urn")
        db.commit()
        
        return RedirectResponse(url=success_url)
    except Exception:
        return RedirectResponse(url=error_url)
