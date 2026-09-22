import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="owner")  # owner, trainer, staff

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="users")

    __table_args__ = (
        Index("ix_users_gym_role", "gym_id", "role"),
    )
