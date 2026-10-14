import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.gym import Gym
from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment
from app.schemas.member import MemberCreate, MemberResponse, MemberListResponse
from app.schemas.membership import MembershipResponse
from app.schemas.membership_plan import MembershipPlanListResponse, MembershipPlanResponse
from app.schemas.payment import PaymentResponse
from app.core.exceptions import FitFlowException, ResourceNotFoundException
from app.services.member_service import _enrich_member_response


class PublicMemberSignupRequest(BaseModel):
    gym_id: uuid.UUID
    plan_id: uuid.UUID
    member: MemberCreate
    payment_method: str = Field(default="upi", max_length=50)
    payment_status: str = Field(default="success", max_length=20)
    payment_reference: str | None = None


router = APIRouter(prefix="/public", tags=["Public Access"])


@router.get("/gyms/{gym_id}/plans", response_model=MembershipPlanListResponse)
async def list_public_plans(
    gym_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    gym = await db.get(Gym, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym", gym_id)

    stmt = (
        select(MembershipPlan)
        .where(MembershipPlan.gym_id == gym_id, MembershipPlan.status == "active")
        .order_by(MembershipPlan.price.asc())
    )
    result = await db.execute(stmt)
    plans = result.scalars().all()

    items = [
        MembershipPlanResponse(
            id=plan.id,
            gym_id=plan.gym_id,
            name=plan.name,
            description=plan.description,
            price=float(plan.price),
            duration_days=plan.duration_days,
            status=plan.status or "active",
            created_at=plan.created_at,
        )
        for plan in plans
    ]
    return MembershipPlanListResponse(items=items, total=len(items))


@router.post("/member-signup", response_model=dict, status_code=status.HTTP_200_OK)
async def public_member_signup(
    payload: PublicMemberSignupRequest,
    db: AsyncSession = Depends(get_db),
):
    if payload.payment_status not in ("success", "paid"):
        raise FitFlowException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="PaymentRequired",
            detail="Payment must succeed before a public signup is registered.",
        )

    gym = await db.get(Gym, payload.gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym", payload.gym_id)

    plan = await db.get(MembershipPlan, payload.plan_id)
    if not plan or plan.gym_id != gym.id:
        raise ResourceNotFoundException("MembershipPlan", payload.plan_id)

    member = Member(
        gym_id=gym.id,
        name=payload.member.name,
        first_name=payload.member.first_name,
        last_name=payload.member.last_name,
        email=payload.member.email,
        phone=payload.member.phone,
        date_of_birth=payload.member.date_of_birth,
        gender=payload.member.gender,
        occupation=payload.member.occupation,
        city=payload.member.city,
        emergency_contact_name=payload.member.emergency_contact_name,
        emergency_contact_phone=payload.member.emergency_contact_phone,
        join_date=payload.member.join_date or date.today(),
        preferred_training_time=payload.member.preferred_training_time,
        fitness_goal=payload.member.fitness_goal,
        acquisition_source=payload.member.acquisition_source,
        referral_source=payload.member.referral_source,
        trainer_id=payload.member.trainer_id,
        status=payload.member.status,
    )
    db.add(member)
    await db.flush()

    start_date = date.today()
    membership = Membership(
        gym_id=gym.id,
        member_id=member.id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=start_date + timedelta(days=plan.duration_days),
        status="active",
    )
    db.add(membership)
    await db.flush()

    now = datetime.now(timezone.utc)
    payment = Payment(
        gym_id=gym.id,
        member_id=member.id,
        membership_id=membership.id,
        amount=plan.price,
        currency="INR",
        status="paid",
        payment_method=payload.payment_method or "upi",
        provider="demo",
        provider_payment_id=payload.payment_reference or f"public-{uuid.uuid4()}",
        payment_link_id=None,
        due_date=date.today(),
        paid_at=now,
        failure_reason=None,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(member)
    await db.refresh(membership)
    await db.refresh(payment)

    member_response = await _enrich_member_response(db, member)
    membership_response = MembershipResponse(
        id=membership.id,
        gym_id=membership.gym_id,
        member_id=membership.member_id,
        member_name=member.name,
        member_email=member.email,
        plan_id=membership.plan_id,
        plan_name=plan.name,
        plan_price=float(plan.price),
        plan_duration_days=plan.duration_days,
        start_date=membership.start_date,
        end_date=membership.end_date,
        status=membership.status,
        created_at=membership.created_at,
    )
    payment_response = PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name,
        member_email=member.email,
        membership_id=payment.membership_id,
        plan_name=plan.name,
        amount=float(payment.amount),
        currency=payment.currency,
        status="paid",
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        payment_link_id=payment.payment_link_id,
        due_date=payment.due_date,
        paid_at=payment.paid_at,
        failure_reason=payment.failure_reason,
        is_recurring=False,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )

    return {
        "member": member_response,
        "membership": membership_response,
        "payment": payment_response,
    }