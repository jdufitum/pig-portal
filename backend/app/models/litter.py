import uuid
from datetime import date

from sqlalchemy import Date, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Litter(Base):
    __tablename__ = "litters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sow_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id"), nullable=True)
    boar_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id"), nullable=True)
    farrow_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    liveborn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stillborn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    neonatal_deaths: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    wean_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        CheckConstraint("liveborn >= 0", name="ck_litters_liveborn_nonneg"),
        CheckConstraint("stillborn >= 0", name="ck_litters_stillborn_nonneg"),
        CheckConstraint("neonatal_deaths >= 0", name="ck_litters_neodeaths_nonneg"),
    )

