from pydantic import BaseModel
from datetime import datetime

class BookingCreate(BaseModel):
    expert_id: int
    slot: datetime

class BookingRead(BaseModel):
    id: int
    user_id: int
    expert_id: int
    slot: datetime
    status: str

    class Config:
        from_attributes = True
