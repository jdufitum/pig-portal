import uuid
from datetime import date

from sqlalchemy import Date, Numeric, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class WeightRecord(Base):
    __tablename__ = "weight_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pig_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    pig = relationship("Pig", back_populates="weight_records")

    __table_args__ = (
        CheckConstraint("weight_kg > 0", name="ck_weight_records_weight_positive"),
    )

