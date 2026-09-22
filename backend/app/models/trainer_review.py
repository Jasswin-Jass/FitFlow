import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.trainer import Trainer
    from app.models.member import Member


class TrainerReview(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trainer_reviews"

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
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    review: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym")
    trainer: Mapped["Trainer"] = relationship("Trainer", back_populates="reviews")
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        Index("ix_trainer_reviews_gym_trainer", "gym_id", "trainer_id"),
    )
