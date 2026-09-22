import uuid
from datetime import date
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Date, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.membership import Membership
    from app.models.payment import Payment
    from app.models.trainer import Trainer
    from app.models.trainer_assignment import TrainerMemberAssignment


class Member(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "members"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Male, Female, Other, Prefer not to say
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    join_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    preferred_training_time: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # Morning, Afternoon, Evening, Night
    fitness_goal: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Weight Loss, Muscle Gain, Endurance, Flexibility, General Fitness
    acquisition_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Walk-in, Referral, Social Media, Google Search, Flyer/Local Ad
    referral_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, inactive
    
    trainer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("trainers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="members")
    trainer: Mapped[Optional["Trainer"]] = relationship("Trainer", back_populates="members")
    trainer_assignments: Mapped[List["TrainerMemberAssignment"]] = relationship("TrainerMemberAssignment", back_populates="member", cascade="all, delete-orphan")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="member", cascade="all, delete-orphan")

    @property
    def age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    __table_args__ = (
        Index("ix_members_gym_status", "gym_id", "status"),
        Index("ix_members_gym_name", "gym_id", "name"),
        Index("ix_members_gym_gender", "gym_id", "gender"),
        Index("ix_members_gym_dob", "gym_id", "date_of_birth"),
        Index("ix_members_gym_source", "gym_id", "acquisition_source"),
    )
