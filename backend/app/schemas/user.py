from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    is_learner: bool
    is_expert: bool
    is_admin: bool

    class Config:
        from_attributes = True


class UserProfileRead(UserRead):
    expert_profile: Optional[dict] = None