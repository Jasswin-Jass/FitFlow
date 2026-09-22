import uuid
from datetime import date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Date, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.user import User
    from app.models.member import Member


class Trainer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trainers"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False)
    years_of_experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    certification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    certification_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    joining_date: Mapped[Optional[date]] = mapped_column(Date, default=date.today, nullable=True)
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time", nullable=False)  # Full-time, Part-time, Contract
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, inactive
    max_client_capacity: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="trainers")
    user: Mapped[Optional["User"]] = relationship("User")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="trainer")

    __table_args__ = (
        Index("ix_trainers_gym_specialty", "gym_id", "specialty"),
        Index("ix_trainers_gym_status", "gym_id", "status"),
    )
