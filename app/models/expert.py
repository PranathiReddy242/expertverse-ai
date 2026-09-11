from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Expert(Base):
    __tablename__ = "experts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    # Professional title
    title = Column(
        String,
        nullable=False
    )

    company = Column(
        String,
        nullable=True
    )

    experience_years = Column(
        Integer,
        default=0
    )

    bio = Column(
        Text,
        nullable=True
    )

    # Comma separated skills
    skills = Column(
        Text,
        nullable=True
    )

    profile_image = Column(
        String,
        nullable=True
    )

    linkedin_url = Column(
        String,
        nullable=True
    )

    github_url = Column(
        String,
        nullable=True
    )

    website_url = Column(
        String,
        nullable=True
    )

    hourly_rate = Column(
        Float,
        default=0.0
    )

    rating = Column(
        Float,
        default=0.0
    )

    total_reviews = Column(
        Integer,
        default=0
    )

    total_sessions = Column(
        Integer,
        default=0
    )

    # Admin verification
    is_verified = Column(
        Boolean,
        default=False
    )

    # pending, approved, rejected
    verification_status = Column(
        String,
        default="pending"
    )

    rejection_reason = Column(
        Text,
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    # Expert controls visibility
    is_active = Column(
        Boolean,
        default=True
    )

    user = relationship(
        "User",
        back_populates="expert_profile"
    )

    availabilities = relationship(
        "Availability",
        back_populates="expert"
    )

    bookings = relationship(
        "Booking",
        back_populates="expert"
    )

    documents = relationship(
        "Document",
        back_populates="expert"
    )