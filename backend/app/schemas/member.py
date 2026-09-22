import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=30)
    occupation: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    join_date: Optional[date] = None
    preferred_training_time: Optional[str] = Field(None, max_length=30)
    fitness_goal: Optional[str] = Field(None, max_length=50)
    acquisition_source: Optional[str] = Field(None, max_length=50)
    referral_source: Optional[str] = Field(None, max_length=100)
    trainer_id: Optional[uuid.UUID] = None
    status: str = Field(default="active", pattern="^(active|inactive)$")

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=30)
    occupation: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    join_date: Optional[date] = None
    preferred_training_time: Optional[str] = Field(None, max_length=30)
    fitness_goal: Optional[str] = Field(None, max_length=50)
    acquisition_source: Optional[str] = Field(None, max_length=50)
    referral_source: Optional[str] = Field(None, max_length=100)
    trainer_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: str
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    join_date: date
    preferred_training_time: Optional[str] = None
    fitness_goal: Optional[str] = None
    acquisition_source: Optional[str] = None
    referral_source: Optional[str] = None
    trainer_id: Optional[uuid.UUID] = None
    trainer_name: Optional[str] = None
    status: str
    membership_plan_name: Optional[str] = None
    membership_start_date: Optional[date] = None
    membership_end_date: Optional[date] = None
    membership_status: Optional[str] = None
    lifetime_value: float = 0.0
    total_payments: int = 0
    average_payment: float = 0.0
    last_payment_date: Optional[date] = None
    renewal_count: int = 0
    is_at_risk: bool = False
    risk_reason: Optional[str] = None
    created_at: datetime


class MemberListResponse(BaseModel):
    items: List[MemberResponse]
    total: int
    page: int
    size: int
    pages: int
