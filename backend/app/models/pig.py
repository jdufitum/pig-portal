import uuid
from datetime import date

from sqlalchemy import String, Date, DateTime, Text, ForeignKey, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Pig(Base):
    __tablename__ = "pigs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ear_tag: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    sex: Mapped[str | None] = mapped_column(SAEnum("M", "F", name="pig_sex", create_type=False), nullable=True)
    breed: Mapped[str | None] = mapped_column(Text, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pig_class: Mapped[str | None] = mapped_column(
        "class", SAEnum("piglet", "grower", "finisher", "sow", "boar", name="pig_class", create_type=False), nullable=True
    )
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "sold", "dead", name="pig_status", create_type=False), nullable=False, server_default="active"
    )
    current_pen: Mapped[str | None] = mapped_column(Text, nullable=True)

    sire_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id", ondelete="SET NULL"), nullable=True)
    dam_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pigs.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    weight_records = relationship("WeightRecord", back_populates="pig", cascade="all, delete-orphan")

