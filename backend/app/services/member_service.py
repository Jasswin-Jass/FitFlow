import uuid
from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload

from app.models.member import Member
from app.models.trainer import Trainer
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberListResponse
from app.core.exceptions import ResourceNotFoundException, TenantAccessDeniedException


async def _enrich_member_response(session: AsyncSession, member: Member) -> MemberResponse:
    # 1. Latest membership for this member
    stmt = (
        select(Membership, MembershipPlan)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(Membership.member_id == member.id)
        .order_by(Membership.created_at.desc())
        .limit(1)
    )
    res = await session.execute(stmt)
    row = res.first()

    plan_name = row[1].name if row else None
    start_date = row[0].start_date if row else None
    end_date = row[0].end_date if row else None
    membership_status = row[0].status if row else None

    # 2. Trainer name
    trainer_name = None
    if member.trainer_id:
        t = await session.get(Trainer, member.trainer_id)
        if t:
            trainer_name = t.name

    # 3. Financial history (LTV, total payments, last payment date)
    pay_stmt = (
        select(func.sum(Payment.amount), func.count(Payment.id), func.max(Payment.paid_at))
        .where(Payment.member_id == member.id, Payment.status == "paid")
    )
    tot_amt, tot_cnt, max_date = (await session.execute(pay_stmt)).one()
    avg_payment = round(float(tot_amt or 0.0) / tot_cnt, 2) if tot_cnt and tot_cnt > 0 else 0.0

    # 4. Renewal count (memberships count - 1 if > 0)
    mship_cnt_stmt = select(func.count(Membership.id)).where(Membership.member_id == member.id)
    mship_cnt = (await session.execute(mship_cnt_stmt)).scalar() or 0
    renewal_count = max(0, mship_cnt - 1)

    # 5. Risk calculation
    today = date.today()
    is_at_risk = False
    risk_reason = None
    if row and row[0].status == "active" and row[0].end_date:
        days_left = (row[0].end_date - today).days
        if 0 <= days_left <= 7:
            is_at_risk = True
            risk_reason = f"Expiring in {days_left} day{'s' if days_left != 1 else ''}"

    if not is_at_risk:
        failed_pay_stmt = select(func.count(Payment.id)).where(
            Payment.member_id == member.id,
            Payment.status == "failed",
        )
        failed_count = (await session.execute(failed_pay_stmt)).scalar() or 0
        if failed_count > 0:
            is_at_risk = True
            risk_reason = "Overdue failed payment"

    return MemberResponse(
        id=member.id,
        gym_id=member.gym_id,
        name=member.name,
        first_name=member.first_name,
        last_name=member.last_name,
        email=member.email,
        phone=member.phone,
        date_of_birth=member.date_of_birth,
        age=member.age,
        gender=member.gender,
        occupation=member.occupation,
        city=member.city,
        emergency_contact_name=member.emergency_contact_name,
        emergency_contact_phone=member.emergency_contact_phone,
        join_date=member.join_date,
        preferred_training_time=member.preferred_training_time,
        fitness_goal=member.fitness_goal,
        acquisition_source=member.acquisition_source,
        referral_source=member.referral_source,
        trainer_id=member.trainer_id,
        trainer_name=trainer_name,
        status=member.status,
        membership_plan_name=plan_name,
        membership_start_date=start_date,
        membership_end_date=end_date,
        membership_status=membership_status,
        lifetime_value=float(tot_amt or 0.0),
        total_payments=tot_cnt or 0,
        average_payment=avg_payment,
        last_payment_date=max_date.date() if max_date else None,
        renewal_count=renewal_count,
        is_at_risk=is_at_risk,
        risk_reason=risk_reason,
        created_at=member.created_at,
    )


async def list_members(
    session: AsyncSession,
    gym_id: uuid.UUID,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> MemberListResponse:
    query = select(Member).where(Member.gym_id == gym_id)

    if status and status in ("active", "inactive"):
        query = query.where(Member.status == status)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Member.name.ilike(search_pattern),
                Member.email.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Member.occupation.ilike(search_pattern),
                Member.city.ilike(search_pattern),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await session.execute(count_query)
    total = total_res.scalar() or 0

    # Pagination
    offset = (page - 1) * size
    query = query.order_by(Member.created_at.desc()).offset(offset).limit(size)
    result = await session.execute(query)
    members = result.scalars().all()

    enriched_items = [await _enrich_member_response(session, m) for m in members]
    pages = (total + size - 1) // size if total > 0 else 1

    return MemberListResponse(
        items=enriched_items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


async def get_member(
    session: AsyncSession, gym_id: uuid.UUID, member_id: uuid.UUID
) -> MemberResponse:
    member = await session.get(Member, member_id)
    if not member:
        raise ResourceNotFoundException("Member", member_id)
    if member.gym_id != gym_id:
        raise TenantAccessDeniedException()

    return await _enrich_member_response(session, member)


async def create_member(
    session: AsyncSession, gym_id: uuid.UUID, data: MemberCreate
) -> MemberResponse:
    member = Member(
        gym_id=gym_id,
        name=data.name,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        occupation=data.occupation,
        city=data.city,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
        join_date=data.join_date or date.today(),
        preferred_training_time=data.preferred_training_time,
        fitness_goal=data.fitness_goal,
        acquisition_source=data.acquisition_source,
        referral_source=data.referral_source,
        trainer_id=data.trainer_id,
        status=data.status,
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return await _enrich_member_response(session, member)


async def update_member(
    session: AsyncSession, gym_id: uuid.UUID, member_id: uuid.UUID, data: MemberUpdate
) -> MemberResponse:
    member = await session.get(Member, member_id)
    if not member:
        raise ResourceNotFoundException("Member", member_id)
    if member.gym_id != gym_id:
        raise TenantAccessDeniedException()

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(member, field, val)

    await session.commit()
    await session.refresh(member)
    return await _enrich_member_response(session, member)


async def delete_member(
    session: AsyncSession, gym_id: uuid.UUID, member_id: uuid.UUID
) -> None:
    member = await session.get(Member, member_id)
    if not member:
        raise ResourceNotFoundException("Member", member_id)
    if member.gym_id != gym_id:
        raise TenantAccessDeniedException()

    await session.delete(member)
    await session.commit()
