import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PaymentCreate(BaseModel):
    member_id: uuid.UUID
    membership_id: Optional[uuid.UUID] = None
    amount: float = Field(..., gt=0)
    status: str = Field(default="success", pattern="^(success|failed|refunded)$")
    paid_at: Optional[datetime] = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    member_id: uuid.UUID
    member_name: Optional[str] = None
    member_email: Optional[str] = None
    membership_id: Optional[uuid.UUID] = None
    plan_name: Optional[str] = None
    amount: float
    paid_at: datetime
    status: str


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int
