from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.member import Member
    from app.models.trainer import Trainer
    from app.models.membership_plan import MembershipPlan
    from app.models.membership import Membership
    from app.models.payment import Payment
    from app.models.summary_metrics import SummaryMetric


class Gym(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gyms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="gym", cascade="all, delete-orphan")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="gym", cascade="all, delete-orphan")
    trainers: Mapped[List["Trainer"]] = relationship("Trainer", back_populates="gym", cascade="all, delete-orphan")
    membership_plans: Mapped[List["MembershipPlan"]] = relationship("MembershipPlan", back_populates="gym", cascade="all, delete-orphan")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="gym", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="gym", cascade="all, delete-orphan")
    summary_metrics: Mapped[List["SummaryMetric"]] = relationship("SummaryMetric", back_populates="gym", cascade="all, delete-orphan")
