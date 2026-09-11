from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
    Float
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Learner
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Expert
    expert_id = Column(
        Integer,
        ForeignKey("experts.id"),
        nullable=False
    )

    # Session start time
    slot = Column(
        DateTime,
        nullable=False
    )

    # Booking workflow
    status = Column(
        String,
        nullable=False,
        default="pending"
    )
    # pending
    # accepted
    # rejected
    # completed
    # cancelled

    # Payment workflow
    payment_status = Column(
        String,
        default="unpaid"
    )
    # unpaid
    # paid
    # refunded

    amount = Column(
        Float,
        default=0.0
    )

    duration_minutes = Column(
        Integer,
        default=60
    )

    meeting_link = Column(
        String,
        nullable=True
    )

    learner_notes = Column(
        String,
        nullable=True
    )

    expert_notes = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="bookings"
    )

    expert = relationship(
        "Expert",
        back_populates="bookings"
    )

    review = relationship(
        "Review",
        back_populates="booking",
        uselist=False
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="booking",
        uselist=False
    )