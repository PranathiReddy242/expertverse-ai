from pydantic import BaseModel


class BecomeExpertResponse(BaseModel):
    message: str
    is_expert: bool