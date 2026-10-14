import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym
    from app.models.member import Member
    from app.models.payment import Payment


class PaymentReminder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payment_reminders"

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
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reminder_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # expiry_7d, expiry_2d, expiry_today, payment_failed, renewal_success
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    channel: Mapped[str] = mapped_column(
        String(50), default="in_app", nullable=False
    )  # in_app, email, sms, whatsapp
    status: Mapped[str] = mapped_column(
        String(50), default="sent", nullable=False
    )  # sent, read, pending

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym")
    member: Mapped["Member"] = relationship("Member")
    payment: Mapped[Optional["Payment"]] = relationship("Payment")

    __table_args__ = (
        Index("ix_reminders_gym_member", "gym_id", "member_id", "reminder_type"),
        Index("ix_reminders_created", "gym_id", "created_at"),
    )
