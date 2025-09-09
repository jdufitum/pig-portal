import uuid
from sqlalchemy import String, DateTime, func, Enum as SAEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserRole:
    OWNER = "owner"
    WORKER = "worker"
    VET = "vet"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(SAEnum('owner','worker','vet', name='user_role', create_type=False))
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)