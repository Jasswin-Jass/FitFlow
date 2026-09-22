import uuid
from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.membership_plan import MembershipPlan
from app.models.membership import Membership
from app.models.member import Member
from app.models.payment import Payment
from app.schemas.membership_plan import (
    MembershipPlanCreate,
    MembershipPlanUpdate,
    MembershipPlanResponse,
    MembershipPlanListResponse,
)
from app.schemas.membership import (
    MembershipCreate,
    MembershipRenew,
    MembershipUpdate,
    MembershipResponse,
    MembershipListResponse,
)
from app.core.exceptions import (
    ResourceNotFoundException,
    TenantAccessDeniedException,
    ValidationException,
)


# ==========================================
# Membership Plans
# ==========================================

async def list_plans(session: AsyncSession, gym_id: uuid.UUID) -> MembershipPlanListResponse:
    stmt = (
        select(MembershipPlan)
        .where(MembershipPlan.gym_id == gym_id)
        .order_by(MembershipPlan.price.asc())
    )
    res = await session.execute(stmt)
    plans = res.scalars().all()
    items = [
        MembershipPlanResponse(
            id=p.id,
            gym_id=p.gym_id,
            name=p.name,
            description=p.description,
            price=float(p.price),
            duration_days=p.duration_days,
            status=p.status or "active",
            created_at=p.created_at,
        )
        for p in plans
    ]
    return MembershipPlanListResponse(items=items, total=len(items))


async def get_plan(
    session: AsyncSession, gym_id: uuid.UUID, plan_id: uuid.UUID
) -> MembershipPlanResponse:
    plan = await session.get(MembershipPlan, plan_id)
    if not plan:
        raise ResourceNotFoundException("MembershipPlan", plan_id)
    if plan.gym_id != gym_id:
        raise TenantAccessDeniedException()

    return MembershipPlanResponse(
        id=plan.id,
        gym_id=plan.gym_id,
        name=plan.name,
        description=plan.description,
        price=float(plan.price),
        duration_days=plan.duration_days,
        status=plan.status or "active",
        created_at=plan.created_at,
    )


async def create_plan(
    session: AsyncSession, gym_id: uuid.UUID, data: MembershipPlanCreate
) -> MembershipPlanResponse:
    plan = MembershipPlan(
        gym_id=gym_id,
        name=data.name,
        description=data.description,
        price=data.price,
        duration_days=data.duration_days,
        status=data.status or "active",
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)

    return MembershipPlanResponse(
        id=plan.id,
        gym_id=plan.gym_id,
        name=plan.name,
        description=plan.description,
        price=float(plan.price),
        duration_days=plan.duration_days,
        status=plan.status or "active",
        created_at=plan.created_at,
    )


async def update_plan(
    session: AsyncSession, gym_id: uuid.UUID, plan_id: uuid.UUID, data: MembershipPlanUpdate
) -> MembershipPlanResponse:
    plan = await session.get(MembershipPlan, plan_id)
    if not plan:
        raise ResourceNotFoundException("MembershipPlan", plan_id)
    if plan.gym_id != gym_id:
        raise TenantAccessDeniedException()

    if data.name is not None:
        plan.name = data.name
    if data.description is not None:
        plan.description = data.description
    if data.price is not None:
        plan.price = data.price
    if data.duration_days is not None:
        plan.duration_days = data.duration_days
    if data.status is not None:
        plan.status = data.status

    await session.commit()
    await session.refresh(plan)

    return MembershipPlanResponse(
        id=plan.id,
        gym_id=plan.gym_id,
        name=plan.name,
        description=plan.description,
        price=float(plan.price),
        duration_days=plan.duration_days,
        status=plan.status or "active",
        created_at=plan.created_at,
    )


async def delete_plan(
    session: AsyncSession, gym_id: uuid.UUID, plan_id: uuid.UUID
) -> None:
    plan = await session.get(MembershipPlan, plan_id)
    if not plan:
        raise ResourceNotFoundException("MembershipPlan", plan_id)
    if plan.gym_id != gym_id:
        raise TenantAccessDeniedException()

    await session.delete(plan)
    await session.commit()


# ==========================================
# Memberships
# ==========================================

async def list_memberships(
    session: AsyncSession,
    gym_id: uuid.UUID,
    status: Optional[str] = None,
) -> MembershipListResponse:
    query = (
        select(Membership, Member, MembershipPlan)
        .join(Member, Membership.member_id == Member.id)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(Membership.gym_id == gym_id)
    )

    if status and status in ("active", "expired", "cancelled"):
        query = query.where(Membership.status == status)

    query = query.order_by(desc(Membership.created_at))
    res = await session.execute(query)
    rows = res.all()

    items = [
        MembershipResponse(
            id=m.id,
            gym_id=m.gym_id,
            member_id=m.member_id,
            member_name=mem.name,
            member_email=mem.email,
            plan_id=m.plan_id,
            plan_name=plan.name,
            plan_price=float(plan.price),
            plan_duration_days=plan.duration_days,
            start_date=m.start_date,
            end_date=m.end_date,
            status=m.status,
            created_at=m.created_at,
        )
        for m, mem, plan in rows
    ]
    return MembershipListResponse(items=items, total=len(items))


async def create_membership(
    session: AsyncSession, gym_id: uuid.UUID, data: MembershipCreate
) -> MembershipResponse:
    # Verify member belongs to this gym
    member = await session.get(Member, data.member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", data.member_id)

    # Verify plan belongs to this gym
    plan = await session.get(MembershipPlan, data.plan_id)
    if not plan or plan.gym_id != gym_id:
        raise ResourceNotFoundException("MembershipPlan", data.plan_id)

    start_date = data.start_date or date.today()
    end_date = start_date + timedelta(days=plan.duration_days)

    membership = Membership(
        gym_id=gym_id,
        member_id=member.id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status="active",
    )
    session.add(membership)
    await session.flush()

    # Automatically record payment if requested
    if data.create_payment:
        payment = Payment(
            gym_id=gym_id,
            member_id=member.id,
            membership_id=membership.id,
            amount=plan.price,
            status="paid",
        )
        session.add(payment)

    # Ensure member status is active
    member.status = "active"

    await session.commit()
    await session.refresh(membership)

    return MembershipResponse(
        id=membership.id,
        gym_id=membership.gym_id,
        member_id=member.id,
        member_name=member.name,
        member_email=member.email,
        plan_id=plan.id,
        plan_name=plan.name,
        plan_price=float(plan.price),
        plan_duration_days=plan.duration_days,
        start_date=membership.start_date,
        end_date=membership.end_date,
        status=membership.status,
        created_at=membership.created_at,
    )


async def renew_membership(
    session: AsyncSession, gym_id: uuid.UUID, membership_id: uuid.UUID, data: MembershipRenew
) -> MembershipResponse:
    old_membership = await session.get(Membership, membership_id)
    if not old_membership:
        raise ResourceNotFoundException("Membership", membership_id)
    if old_membership.gym_id != gym_id:
        raise TenantAccessDeniedException()

    plan_id = data.plan_id or old_membership.plan_id
    plan = await session.get(MembershipPlan, plan_id)
    if not plan or plan.gym_id != gym_id:
        raise ResourceNotFoundException("MembershipPlan", plan_id)

    # Start date defaults to the day after current membership ends or today, whichever is later
    if data.start_date:
        start_date = data.start_date
    else:
        start_date = max(date.today(), old_membership.end_date + timedelta(days=1))

    end_date = start_date + timedelta(days=plan.duration_days)

    new_membership = Membership(
        gym_id=gym_id,
        member_id=old_membership.member_id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status="active",
    )
    session.add(new_membership)
    await session.flush()

    if data.create_payment:
        payment = Payment(
            gym_id=gym_id,
            member_id=old_membership.member_id,
            membership_id=new_membership.id,
            amount=plan.price,
            status="paid",
        )
        session.add(payment)

    member = await session.get(Member, old_membership.member_id)
    if member:
        member.status = "active"

    await session.commit()
    await session.refresh(new_membership)

    return MembershipResponse(
        id=new_membership.id,
        gym_id=new_membership.gym_id,
        member_id=old_membership.member_id,
        member_name=member.name if member else "",
        member_email=member.email if member else "",
        plan_id=plan.id,
        plan_name=plan.name,
        plan_price=float(plan.price),
        plan_duration_days=plan.duration_days,
        start_date=new_membership.start_date,
        end_date=new_membership.end_date,
        status=new_membership.status,
        created_at=new_membership.created_at,
    )


async def update_membership(
    session: AsyncSession, gym_id: uuid.UUID, membership_id: uuid.UUID, data: MembershipUpdate
) -> MembershipResponse:
    membership = await session.get(Membership, membership_id)
    if not membership:
        raise ResourceNotFoundException("Membership", membership_id)
    if membership.gym_id != gym_id:
        raise TenantAccessDeniedException()

    if data.status is not None:
        membership.status = data.status
    if data.end_date is not None:
        if data.end_date < membership.start_date:
            raise ValidationException("Membership end date cannot be before start date")
        membership.end_date = data.end_date

    await session.commit()
    await session.refresh(membership)

    member = await session.get(Member, membership.member_id)
    plan = await session.get(MembershipPlan, membership.plan_id)

    return MembershipResponse(
        id=membership.id,
        gym_id=membership.gym_id,
        member_id=membership.member_id,
        member_name=member.name if member else "",
        member_email=member.email if member else "",
        plan_id=membership.plan_id,
        plan_name=plan.name if plan else "",
        plan_price=float(plan.price) if plan else None,
        plan_duration_days=plan.duration_days if plan else None,
        start_date=membership.start_date,
        end_date=membership.end_date,
        status=membership.status,
        created_at=membership.created_at,
    )
