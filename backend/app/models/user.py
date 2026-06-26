from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    # Multiple roles supported
    is_learner = Column(Boolean, default=True)
    is_expert = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    expert_profile = relationship(
        "Expert",
        back_populates="user",
        uselist=False
    )

    bookings = relationship(
        "Booking",
        back_populates="user"
    )

    chat_history = relationship(
        "ChatHistory",
        back_populates="user"
    )