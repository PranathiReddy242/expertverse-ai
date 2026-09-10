from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: str = "user"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserRead(UserBase):
    id: int
    is_learner: bool = True
    is_expert: bool = False
    is_admin: bool = False

    class Config:
        from_attributes = True


class UserProfileRead(UserRead):
    expert_profile: Optional[dict] = None
