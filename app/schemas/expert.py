from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserRead

class ExpertBase(BaseModel):
    title: str
    company: Optional[str] = None
    experience_years: int = 0
    bio: Optional[str] = None
    skills: Optional[str] = None
    profile_image: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    hourly_rate: float = 0.0

class ExpertCreate(ExpertBase):
    pass

class ExpertRead(ExpertBase):
    id: int
    user_id: int
    rating: float
    total_reviews: int = 0
    total_sessions: int = 0
    is_verified: bool = False
    verification_status: str = "pending"
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    is_active: bool = True
    user: Optional[UserRead] = None

    class Config:
        from_attributes = True

class ExpertVerificationSubmit(BaseModel):
    certificate_url: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    experience_years: Optional[int] = None
    notes: Optional[str] = None

class ExpertReviewAction(BaseModel):
    reason: Optional[str] = None
