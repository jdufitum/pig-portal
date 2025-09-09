import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pig_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(SAEnum("photo", "doc", name="file_kind", create_type=False), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

