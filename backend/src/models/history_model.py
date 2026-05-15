import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.clients.db.database import Base


class HistoryModel(Base):
    __tablename__ = "histories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    person_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    dataset_image: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    captured_image: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    is_real: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    is_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "UserModel",
        back_populates="histories"
    )