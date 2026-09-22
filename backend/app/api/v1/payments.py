from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentListResponse
from app.services.payment_service import list_payments, record_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=PaymentListResponse)
async def get_payments(
    status: Optional[str] = Query(None, description="Filter by status: success, failed, refunded"),
    start_date: Optional[date] = Query(None, description="Filter payments from date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter payments up to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_payments(
        db,
        gym_id=current_user.gym_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size,
    )


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def add_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await record_payment(db, gym_id=current_user.gym_id, data=data)
