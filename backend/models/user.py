import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Uuid
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    instagram_access_token = Column(String, nullable=True)
    instagram_refresh_token = Column(String, nullable=True)
    instagram_account_id = Column(String, nullable=True)
    
    linkedin_access_token = Column(String, nullable=True)
    linkedin_refresh_token = Column(String, nullable=True)
    linkedin_author_urn = Column(String, nullable=True)
    last_processed_reel_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
