from pydantic import BaseModel
from datetime import datetime

class ChatHistoryRead(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True
