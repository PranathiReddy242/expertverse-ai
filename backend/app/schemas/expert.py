from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserRead

class ExpertBase(BaseModel):
    title: str
    company: Optional[str] = None
    experience_years: int = 0
    bio: Optional[str] = None
    hourly_rate: float = 0.0

class ExpertCreate(ExpertBase):
    pass

class ExpertRead(ExpertBase):
    id: int
    user_id: int
    rating: float
    user: Optional[UserRead] = None

    class Config:
        from_attributes = True
