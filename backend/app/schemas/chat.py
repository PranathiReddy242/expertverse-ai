from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    recommended_experts: list[dict] = []
    roadmap: dict | None = None
