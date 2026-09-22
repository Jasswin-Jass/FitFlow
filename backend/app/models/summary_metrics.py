import uuid
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Date, Integer, Numeric, ForeignKey, Uuid, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.gym import Gym


class SummaryMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "summary_metrics"

    gym_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    active_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mrr: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    renewal_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True, default=None)
    at_risk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    churned_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    gym: Mapped["Gym"] = relationship("Gym", back_populates="summary_metrics")

    __table_args__ = (
        UniqueConstraint("gym_id", "metric_date", name="uq_summary_metrics_gym_date"),
        Index("ix_summary_metrics_gym_date", "gym_id", "metric_date"),
    )
