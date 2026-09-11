from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    # Session summary
    summary = Column(
        Text,
        nullable=True
    )

    # Action items for learner
    action_items = Column(
        Text,
        nullable=True
    )

    # Homework or assignments
    homework = Column(
        Text,
        nullable=True
    )

    # Resources shared by expert
    resources = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    booking = relationship(
        "Booking",
        back_populates="meeting_notes"
    )
