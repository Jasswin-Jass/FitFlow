import uuid
from datetime import date
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Date, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.member import Member
    from app.models.membership_plan import MembershipPlan
    from app.models.payment import Payment


class Membership(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memberships"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("membership_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, expired, cancelled

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="memberships")
    member: Mapped["Member"] = relationship("Member", back_populates="memberships")
    plan: Mapped["MembershipPlan"] = relationship("MembershipPlan", back_populates="memberships")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="membership")

    __table_args__ = (
        Index("ix_memberships_gym_status_dates", "gym_id", "status", "start_date", "end_date"),
        Index("ix_memberships_member_status", "member_id", "status"),
    )
