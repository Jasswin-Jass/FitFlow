import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.trainer import Trainer
    from app.models.member import Member


class TrainerMemberAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trainer_member_assignments"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trainer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("trainers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # active, ended
        nullable=False,
    )

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym")
    trainer: Mapped["Trainer"] = relationship("Trainer", back_populates="assignments")
    member: Mapped["Member"] = relationship("Member", back_populates="trainer_assignments")

    __table_args__ = (
        Index("ix_trainer_assignments_gym_trainer", "gym_id", "trainer_id", "status"),
        Index("ix_trainer_assignments_gym_member", "gym_id", "member_id", "status"),
    )
