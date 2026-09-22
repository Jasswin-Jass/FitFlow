import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class TrainerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=7, max_length=50)
    specialty: str = Field(..., min_length=2, max_length=255)
    years_of_experience: int = Field(default=0, ge=0)
    certification: Optional[str] = Field(None, max_length=255)
    certification_level: Optional[str] = Field(None, max_length=100)
    joining_date: Optional[date] = None
    employment_type: str = Field(default="Full-time", max_length=50)
    status: str = Field(default="active", pattern="^(active|inactive)$")
    max_client_capacity: int = Field(default=20, ge=1, le=100)
    rating: float = Field(default=5.0, ge=1.0, le=5.0)
    user_id: Optional[uuid.UUID] = None


class TrainerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=50)
    specialty: Optional[str] = Field(None, min_length=2, max_length=255)
    years_of_experience: Optional[int] = Field(None, ge=0)
    certification: Optional[str] = Field(None, max_length=255)
    certification_level: Optional[str] = Field(None, max_length=100)
    joining_date: Optional[date] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    max_client_capacity: Optional[int] = Field(None, ge=1, le=100)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)


class TrainerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    years_of_experience: int = 0
    certification: Optional[str] = None
    certification_level: Optional[str] = None
    joining_date: Optional[date] = None
    employment_type: str = "Full-time"
    status: str = "active"
    max_client_capacity: int = 20
    rating: float = 5.0
    assigned_clients_count: int = 0
    client_load_percent: float = 0.0
    revenue_generated: float = 0.0
    retention_rate: Optional[float] = None
    created_at: datetime


class TrainerListResponse(BaseModel):
    items: List[TrainerResponse]
    total: int
