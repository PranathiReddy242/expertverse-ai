from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    expert_id: int
    slot: datetime
    duration_minutes: Optional[int] = 60
    learner_notes: Optional[str] = None

class BookingRead(BaseModel):
    id: int
    user_id: int
    expert_id: int
    slot: datetime
    status: str
    payment_status: str
    amount: float
    duration_minutes: Optional[int] = 60
    meeting_link: Optional[str] = None
    learner_notes: Optional[str] = None
    expert_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
