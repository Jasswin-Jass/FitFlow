import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PaymentCreate(BaseModel):
    member_id: uuid.UUID
    membership_id: Optional[uuid.UUID] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=10)
    payment_method: Optional[str] = Field(default="upi", max_length=50)
    due_date: Optional[date] = None
    status: Optional[str] = Field(
        default="pending", pattern="^(pending|processing|paid|failed|cancelled|refunded|success)$"
    )
    paid_at: Optional[datetime] = None


class PaymentSimulateFailureRequest(BaseModel):
    failure_reason: Optional[str] = Field(
        default="Transaction declined by issuing bank / UPI timeout", max_length=500
    )


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
    currency: str = "INR"
    status: str
    payment_method: Optional[str] = "upi"
    provider: str = "demo"
    provider_payment_id: Optional[str] = None
    payment_link_id: Optional[str] = None
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    is_recurring: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int


class AutoRenewalEnableRequest(BaseModel):
    member_id: uuid.UUID
    membership_id: Optional[uuid.UUID] = None


class AutoRenewalSimulateRequest(BaseModel):
    failure_reason: Optional[str] = Field(
        default="Recurring mandate limit exceeded / bank network timeout", max_length=500
    )


class PaymentSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    member_id: uuid.UUID
    member_name: Optional[str] = None
    member_email: Optional[str] = None
    membership_id: uuid.UUID
    plan_name: Optional[str] = None
    provider: str = "demo"
    provider_subscription_id: Optional[str] = None
    amount: float
    currency: str = "INR"
    billing_interval: str = "monthly"
    status: str
    start_date: date
    next_billing_date: date
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class DuePaymentsProcessResponse(BaseModel):
    processed: int
    succeeded: int
    failed: int
    total_collected: float
    details: List[Dict[str, Any]] = []


class PaymentReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    member_id: uuid.UUID
    member_name: Optional[str] = None
    payment_id: Optional[uuid.UUID] = None
    reminder_type: str
    title: str
    message: str
    channel: str
    status: str
    created_at: datetime


class AutomationStatusResponse(BaseModel):
    provider: str
    reminders_enabled: bool
    rules: List[Dict[str, Any]]
    active_subscriptions_count: int
    due_subscriptions_count: int
    recent_reminders: List[PaymentReminderResponse]
