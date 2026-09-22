import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MembershipPlanCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)
    status: Optional[str] = Field("active", pattern="^(active|inactive)$")


class MembershipPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class MembershipPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int
    status: str = "active"
    created_at: datetime


class MembershipPlanListResponse(BaseModel):
    items: List[MembershipPlanResponse]
    total: int
