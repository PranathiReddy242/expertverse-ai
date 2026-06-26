from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ExpertVerification(Base):
    __tablename__ = "expert_verifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    certificate_url = Column(String)
    resume_url = Column(String)
    linkedin_url = Column(String)

    experience_years = Column(Integer)

    status = Column(
        String,
        default="pending"
    )
    # pending
    # approved
    # rejected

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship("User")