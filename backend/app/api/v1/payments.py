import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    PaymentSimulateFailureRequest,
    AutoRenewalEnableRequest,
    AutoRenewalSimulateRequest,
    PaymentSubscriptionResponse,
)
from app.services.payment_service import (
    list_payments,
    get_payment,
    create_payment,
    simulate_payment_success,
    simulate_payment_failure,
    cancel_payment,
    retry_payment,
    enable_auto_renewal,
    cancel_auto_renewal,
    get_member_subscription,
    simulate_recurring_success,
    simulate_recurring_failure,
)

router = APIRouter(prefix="/payments", tags=["Payments & Auto-Renewal"])


@router.get("", response_model=PaymentListResponse)
async def get_payments_list(
    status: Optional[str] = Query(None, description="Filter: all, paid, pending, failed, cancelled"),
    member_id: Optional[uuid.UUID] = Query(None, description="Filter by member ID"),
    start_date: Optional[date] = Query(None, description="Filter payments from date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter payments up to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_payments(
        db,
        gym_id=current_user.gym_id,
        status=status,
        member_id=member_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_details(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_payment(db, gym_id=current_user.gym_id, payment_id=payment_id)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
@router.post("/create", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new one-time payment transaction (e.g. for membership activation or dues).
    """
    return await create_payment(db, gym_id=current_user.gym_id, data=data)


@router.post("/{payment_id}/simulate-success", response_model=PaymentResponse)
async def simulate_success_endpoint(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test: Simulates instant successful completion of a pending payment.
    Server verifies payment, marks paid, extends/activates membership, and logs audit notification.
    """
    return await simulate_payment_success(db, gym_id=current_user.gym_id, payment_id=payment_id)


@router.post("/{payment_id}/simulate-failure", response_model=PaymentResponse)
async def simulate_failure_endpoint(
    payment_id: uuid.UUID,
    payload: Optional[PaymentSimulateFailureRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test: Simulates failed transaction (bank decline / UPI timeout).
    Server marks payment failed, preserves membership state without extension, and flags at-risk.
    """
    reason = payload.failure_reason if payload else "Transaction declined by issuing bank / UPI timeout"
    return await simulate_payment_failure(
        db, gym_id=current_user.gym_id, payment_id=payment_id, failure_reason=reason
    )


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment_endpoint(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancels a pending payment transaction.
    """
    return await cancel_payment(db, gym_id=current_user.gym_id, payment_id=payment_id)


@router.post("/{payment_id}/retry", response_model=PaymentResponse)
async def retry_payment_endpoint(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retries a failed or cancelled payment by resetting it to pending.
    """
    return await retry_payment(db, gym_id=current_user.gym_id, payment_id=payment_id)


# =========================================================================
# AUTO RENEWAL MANDATES
# =========================================================================


@router.post("/auto-renewal", response_model=PaymentSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def enable_auto_renewal_endpoint(
    data: AutoRenewalEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a recurring payment mandate/subscription for a gym member.
    """
    return await enable_auto_renewal(
        db,
        gym_id=current_user.gym_id,
        member_id=data.member_id,
        membership_id=data.membership_id,
    )


@router.get("/auto-renewal/{member_id}", response_model=Optional[PaymentSubscriptionResponse])
async def get_auto_renewal_status(
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the current recurring auto-renewal subscription mandate for a member.
    """
    return await get_member_subscription(db, gym_id=current_user.gym_id, member_id=member_id)


@router.post("/auto-renewal/{subscription_id}/cancel", response_model=PaymentSubscriptionResponse)
async def cancel_auto_renewal_endpoint(
    subscription_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancels a recurring payment mandate.
    """
    return await cancel_auto_renewal(db, gym_id=current_user.gym_id, subscription_id=subscription_id)


@router.post("/auto-renewal/{subscription_id}/simulate-success", response_model=PaymentSubscriptionResponse)
async def simulate_recurring_success_endpoint(
    subscription_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test: Simulates successful execution of a recurring billing cycle.
    Creates paid payment, extends membership by plan duration, and advances next billing date.
    """
    return await simulate_recurring_success(db, gym_id=current_user.gym_id, subscription_id=subscription_id)


@router.post("/auto-renewal/{subscription_id}/simulate-failure", response_model=PaymentSubscriptionResponse)
async def simulate_recurring_failure_endpoint(
    subscription_id: uuid.UUID,
    payload: Optional[AutoRenewalSimulateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test: Simulates failed recurring mandate debit.
    Creates failed payment record, marks subscription past_due, and preserves membership duration.
    """
    reason = payload.failure_reason if payload else "Recurring mandate charge declined by bank"
    return await simulate_recurring_failure(
        db, gym_id=current_user.gym_id, subscription_id=subscription_id, failure_reason=reason
    )
