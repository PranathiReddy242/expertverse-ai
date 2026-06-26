from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ExpertPricing(Base):
    __tablename__ = "expert_pricing"

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

    duration_minutes = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    expert = relationship(
        "Expert"
    )