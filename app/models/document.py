from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Text,
    DateTime
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"

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

    # File path / cloud URL
    file_url = Column(
        String,
        nullable=True
    )

    # pdf, txt, docx, md, image, etc.
    file_type = Column(
        String,
        nullable=False
    )

    # Extracted text
    text = Column(
        Text,
        nullable=True
    )

    # Optional title
    title = Column(
        String,
        nullable=True
    )

    # Description
    description = Column(
        Text,
        nullable=True
    )

    # Category
    category = Column(
        String,
        nullable=True
    )
    # resume
    # certificate
    # notes
    # article
    # ebook
    # transcript

    # Document review lifecycle
    status = Column(
        String,
        default="approved"
    )
    # pending
    # approved
    # rejected

    review_notes = Column(
        Text,
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    expert = relationship(
        "Expert",
        back_populates="documents"
    )
