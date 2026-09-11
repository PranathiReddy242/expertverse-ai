from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    String,
    Boolean,
    DateTime
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # AI generated roadmap JSON
    plan_json = Column(
        Text,
        nullable=False
    )

    # Goal name
    title = Column(
        String,
        nullable=True
    )

    # Active / completed
    is_completed = Column(
        Boolean,
        default=False
    )

    # Progress percentage
    progress = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User"
    )
