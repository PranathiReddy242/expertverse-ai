from sqlalchemy import (
    Column,
    Integer,
    Date,
    Time,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Availability(Base):
    __tablename__ = "availability"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    expert_id = Column(
        Integer,
        ForeignKey("experts.id"),
        nullable=False
    )

    # Example: 2026-06-20
    date = Column(
        Date,
        nullable=False
    )

    # Example: 18:00
    start_time = Column(
        Time,
        nullable=False
    )

    # Example: 19:00
    end_time = Column(
        Time,
        nullable=False
    )

    # Prevent double bookings
    is_available = Column(
        Boolean,
        default=True
    )

    expert = relationship(
        "Expert",
        back_populates="availabilities"
    )