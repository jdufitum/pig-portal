import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Text, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    link_type: Mapped[str | None] = mapped_column(SAEnum("pig", "litter", name="task_link_type", create_type=False), nullable=True)
    link_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum("open", "done", name="task_status", create_type=False), nullable=False, server_default="open")
    priority: Mapped[str] = mapped_column(SAEnum("low", "med", "high", name="task_priority", create_type=False), nullable=False, server_default="med")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

