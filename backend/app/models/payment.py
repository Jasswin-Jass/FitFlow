import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.member import Member
    from app.models.membership import Membership


class Payment(Base, UUIDMixin):
    __tablename__ = "payments"

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
    membership_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("memberships.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), default="success", nullable=False)  # success, failed, refunded

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="payments")
    member: Mapped["Member"] = relationship("Member", back_populates="payments")
    membership: Mapped[Optional["Membership"]] = relationship("Membership", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_gym_status_date", "gym_id", "status", "paid_at"),
        Index("ix_payments_member_status", "member_id", "status"),
    )
