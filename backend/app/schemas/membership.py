import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MembershipCreate(BaseModel):
    member_id: uuid.UUID
    plan_id: uuid.UUID
    start_date: Optional[date] = None
    create_payment: bool = True


class MembershipRenew(BaseModel):
    plan_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    create_payment: bool = True


class MembershipUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(active|expired|cancelled)$")
    end_date: Optional[date] = None


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    member_id: uuid.UUID
    member_name: Optional[str] = None
    member_email: Optional[str] = None
    plan_id: uuid.UUID
    plan_name: Optional[str] = None
    plan_price: Optional[float] = None
    plan_duration_days: Optional[int] = None
    start_date: date
    end_date: date
    status: str
    created_at: datetime


class MembershipListResponse(BaseModel):
    items: List[MembershipResponse]
    total: int
