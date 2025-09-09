import uuid
from datetime import date

from sqlalchemy import Date, Text, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class BreedingEvent(Base):
    __tablename__ = "breeding_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sow_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id"), nullable=True)
    boar_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id"), nullable=True)
    service_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    method: Mapped[str] = mapped_column(SAEnum("natural", "ai", name="service_method", create_type=False), nullable=False, server_default="natural")
    expected_farrow: Mapped[date | None] = mapped_column(Date, nullable=True)
    preg_check_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    preg_status: Mapped[str] = mapped_column(SAEnum("pos", "neg", "unknown", name="preg_status", create_type=False), nullable=False, server_default="unknown")
    parity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pen_at_service: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

