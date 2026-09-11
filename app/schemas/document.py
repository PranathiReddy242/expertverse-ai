from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    expert_id: int
    text: str
    file_type: str = "text"
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class DocumentRead(BaseModel):
    id: int
    expert_id: int
    file_url: Optional[str] = None
    file_type: str
    text: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: str = "approved"
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentReview(BaseModel):
    status: str  # approved or rejected
    review_notes: Optional[str] = None
