import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


class TrainerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=7, max_length=50)
    specialty: Optional[str] = Field(None, max_length=255)
    specialization: Optional[str] = Field(None, max_length=255)
    years_of_experience: Optional[int] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    certification: Optional[str] = Field(None, max_length=255)
    certification_level: Optional[str] = Field(None, max_length=100)
    joining_date: Optional[date] = None
    employment_type: str = Field(default="Full-time", max_length=50)
    status: str = Field(default="active", pattern="^(active|inactive)$")
    max_client_capacity: int = Field(default=20, ge=1, le=100)
    bio: Optional[str] = Field(None, max_length=1000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    user_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.specialty and self.specialization:
            self.specialty = self.specialization
        elif not self.specialty:
            self.specialty = "General Fitness"

        if self.years_of_experience is None:
            self.years_of_experience = self.experience_years if self.experience_years is not None else 0
        return self


class TrainerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=50)
    specialty: Optional[str] = Field(None, min_length=2, max_length=255)
    specialization: Optional[str] = Field(None, min_length=2, max_length=255)
    years_of_experience: Optional[int] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    certification: Optional[str] = Field(None, max_length=255)
    certification_level: Optional[str] = Field(None, max_length=100)
    joining_date: Optional[date] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    max_client_capacity: Optional[int] = Field(None, ge=1, le=100)
    bio: Optional[str] = Field(None, max_length=1000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.specialty and self.specialization:
            self.specialty = self.specialization
        if self.years_of_experience is None and self.experience_years is not None:
            self.years_of_experience = self.experience_years
        return self


class TrainerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    gym_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    specialization: Optional[str] = None
    years_of_experience: int = 0
    experience_years: int = 0
    certification: Optional[str] = None
    certification_level: Optional[str] = None
    joining_date: Optional[date] = None
    employment_type: str = "Full-time"
    status: str = "active"
    max_client_capacity: int = 20
    bio: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    assigned_clients_count: int = 0
    client_load_percent: float = 0.0
    revenue_generated: float = 0.0
    retention_rate: Optional[float] = None
    created_at: datetime


class TrainerListResponse(BaseModel):
    items: List[TrainerResponse]
    total: int


class TrainerClientItem(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    name: str
    email: str
    phone: str
    age: Optional[int] = None
    gender: Optional[str] = None
    membership_plan_name: Optional[str] = None
    membership_status: Optional[str] = None
    membership_end_date: Optional[date] = None
    assigned_at: datetime
    status: str


class TrainerClientListResponse(BaseModel):
    items: List[TrainerClientItem]
    total: int


class TrainerClientAssignRequest(BaseModel):
    member_id: uuid.UUID


class TrainerReviewCreate(BaseModel):
    member_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=1000)


class TrainerReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trainer_id: uuid.UUID
    member_id: uuid.UUID
    member_name: Optional[str] = None
    rating: int
    review: Optional[str] = None
    created_at: datetime


class TrainerReviewListResponse(BaseModel):
    items: List[TrainerReviewResponse]
    total: int
    average_rating: Optional[float] = None
