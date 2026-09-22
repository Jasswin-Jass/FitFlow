import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Numeric, Integer, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.membership import Membership


class MembershipPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "membership_plans"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="membership_plans")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="plan")

    __table_args__ = (
        Index("ix_membership_plans_gym_name", "gym_id", "name"),
    )
