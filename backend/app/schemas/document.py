from pydantic import BaseModel

class DocumentCreate(BaseModel):
    expert_id: int
    text: str
    file_type: str = "text"

class DocumentRead(BaseModel):
    id: int
    expert_id: int
    file_url: str | None = None
    file_type: str
    text: str | None = None

    class Config:
        from_attributes = True
