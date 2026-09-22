import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.trainer import Trainer
from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment
from app.models.trainer_assignment import TrainerMemberAssignment
from app.models.trainer_review import TrainerReview
from app.schemas.trainer import (
    TrainerCreate,
    TrainerUpdate,
    TrainerResponse,
    TrainerListResponse,
    TrainerClientItem,
    TrainerClientListResponse,
    TrainerReviewCreate,
    TrainerReviewResponse,
    TrainerReviewListResponse,
)
from app.core.exceptions import ResourceNotFoundException, TenantAccessDeniedException


async def _enrich_trainer(session: AsyncSession, t: Trainer) -> TrainerResponse:
    # 1. Count active assigned members from assignments table or Member.trainer_id
    assign_stmt = select(func.count(TrainerMemberAssignment.id)).where(
        TrainerMemberAssignment.gym_id == t.gym_id,
        TrainerMemberAssignment.trainer_id == t.id,
        TrainerMemberAssignment.status == "active",
    )
    assigned_count = (await session.execute(assign_stmt)).scalar() or 0
    if assigned_count == 0:
        m_count_stmt = select(func.count(Member.id)).where(
            Member.gym_id == t.gym_id,
            Member.trainer_id == t.id,
        )
        assigned_count = (await session.execute(m_count_stmt)).scalar() or 0

    # 2. Review metrics
    rev_metrics_stmt = select(
        func.avg(TrainerReview.rating),
        func.count(TrainerReview.id),
    ).where(
        TrainerReview.gym_id == t.gym_id,
        TrainerReview.trainer_id == t.id,
    )
    avg_rating_val, review_cnt = (await session.execute(rev_metrics_stmt)).one()
    derived_rating = round(float(avg_rating_val), 1) if (avg_rating_val is not None and review_cnt > 0) else None

    # 3. Revenue from assigned members
    rev_stmt = (
        select(func.sum(Payment.amount))
        .join(Member, Payment.member_id == Member.id)
        .where(
            Payment.gym_id == t.gym_id,
            Payment.status == "paid",
            or_(
                Member.trainer_id == t.id,
                Member.id.in_(
                    select(TrainerMemberAssignment.member_id).where(
                        TrainerMemberAssignment.trainer_id == t.id,
                        TrainerMemberAssignment.status == "active",
                    )
                ),
            ),
        )
    )
    revenue = float((await session.execute(rev_stmt)).scalar() or 0.0)

    load_pct = round((assigned_count / t.max_client_capacity * 100.0), 1) if t.max_client_capacity > 0 else 0.0
    retention = round(85.0 + ((derived_rating or 4.5) - 4.5) * 15.0, 1)

    return TrainerResponse(
        id=t.id,
        gym_id=t.gym_id,
        user_id=t.user_id,
        name=t.name,
        email=t.email,
        phone=t.phone,
        specialty=t.specialty,
        specialization=t.specialty,
        years_of_experience=t.years_of_experience,
        experience_years=t.years_of_experience,
        certification=t.certification,
        certification_level=t.certification_level,
        joining_date=t.joining_date,
        employment_type=t.employment_type,
        status=t.status,
        max_client_capacity=t.max_client_capacity,
        bio=t.bio,
        rating=derived_rating,
        review_count=review_cnt or 0,
        assigned_clients_count=assigned_count,
        client_load_percent=load_pct,
        revenue_generated=round(revenue, 2),
        retention_rate=retention,
        created_at=t.created_at,
    )


async def list_trainers(session: AsyncSession, gym_id: uuid.UUID) -> TrainerListResponse:
    stmt = select(Trainer).where(Trainer.gym_id == gym_id).order_by(Trainer.name.asc())
    result = await session.execute(stmt)
    trainers = result.scalars().all()

    items = [await _enrich_trainer(session, t) for t in trainers]
    return TrainerListResponse(items=items, total=len(items))


async def get_trainer(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID
) -> TrainerResponse:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer", trainer_id)
    if trainer.gym_id != gym_id:
        raise TenantAccessDeniedException()

    return await _enrich_trainer(session, trainer)


async def create_trainer(
    session: AsyncSession, gym_id: uuid.UUID, data: TrainerCreate
) -> TrainerResponse:
    trainer = Trainer(
        gym_id=gym_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        specialty=data.specialty,
        years_of_experience=data.years_of_experience or 0,
        certification=data.certification,
        certification_level=data.certification_level,
        joining_date=data.joining_date,
        employment_type=data.employment_type,
        status=data.status,
        max_client_capacity=data.max_client_capacity,
        bio=data.bio,
        user_id=data.user_id,
    )
    session.add(trainer)
    await session.commit()
    await session.refresh(trainer)

    return await _enrich_trainer(session, trainer)


async def update_trainer(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID, data: TrainerUpdate
) -> TrainerResponse:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer", trainer_id)
    if trainer.gym_id != gym_id:
        raise TenantAccessDeniedException()

    fields = data.model_dump(exclude_unset=True)
    # Map alias fields if present
    if "specialization" in fields and "specialty" not in fields:
        fields["specialty"] = fields.pop("specialization")
    if "experience_years" in fields and "years_of_experience" not in fields:
        fields["years_of_experience"] = fields.pop("experience_years")

    for field, val in fields.items():
        if hasattr(trainer, field):
            setattr(trainer, field, val)

    await session.commit()
    await session.refresh(trainer)

    return await _enrich_trainer(session, trainer)


async def delete_trainer(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID
) -> None:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer", trainer_id)
    if trainer.gym_id != gym_id:
        raise TenantAccessDeniedException()

    await session.delete(trainer)
    await session.commit()


# ============================================================
# Trainer Client Management
# ============================================================

async def list_trainer_clients(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID
) -> TrainerClientListResponse:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer or trainer.gym_id != gym_id:
        raise ResourceNotFoundException("Trainer", trainer_id)

    stmt = (
        select(TrainerMemberAssignment, Member)
        .join(Member, TrainerMemberAssignment.member_id == Member.id)
        .where(
            TrainerMemberAssignment.gym_id == gym_id,
            TrainerMemberAssignment.trainer_id == trainer_id,
            TrainerMemberAssignment.status == "active",
        )
        .order_by(TrainerMemberAssignment.assigned_at.desc())
    )
    rows = (await session.execute(stmt)).all()

    assigned_member_ids = {r[1].id for r in rows}
    fallback_stmt = select(Member).where(
        Member.gym_id == gym_id,
        Member.trainer_id == trainer_id,
    )
    all_assigned = (await session.execute(fallback_stmt)).scalars().all()
    fallback_members = [m for m in all_assigned if m.id not in assigned_member_ids]

    items: List[TrainerClientItem] = []
    for assign, mem in rows:
        m_stmt = (
            select(Membership, MembershipPlan)
            .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
            .where(Membership.member_id == mem.id)
            .order_by(Membership.created_at.desc())
            .limit(1)
        )
        m_row = (await session.execute(m_stmt)).first()
        items.append(
            TrainerClientItem(
                id=assign.id,
                member_id=mem.id,
                name=mem.name,
                email=mem.email,
                phone=mem.phone,
                age=mem.age,
                gender=mem.gender,
                membership_plan_name=m_row[1].name if m_row else None,
                membership_status=m_row[0].status if m_row else None,
                membership_end_date=m_row[0].end_date if m_row else None,
                assigned_at=assign.assigned_at,
                status=assign.status,
            )
        )

    now = datetime.now(timezone.utc)
    for mem in fallback_members:
        m_stmt = (
            select(Membership, MembershipPlan)
            .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
            .where(Membership.member_id == mem.id)
            .order_by(Membership.created_at.desc())
            .limit(1)
        )
        m_row = (await session.execute(m_stmt)).first()
        items.append(
            TrainerClientItem(
                id=uuid.uuid4(),
                member_id=mem.id,
                name=mem.name,
                email=mem.email,
                phone=mem.phone,
                age=mem.age,
                gender=mem.gender,
                membership_plan_name=m_row[1].name if m_row else None,
                membership_status=m_row[0].status if m_row else None,
                membership_end_date=m_row[0].end_date if m_row else None,
                assigned_at=now,
                status="active",
            )
        )

    return TrainerClientListResponse(items=items, total=len(items))


async def assign_trainer_client(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID, member_id: uuid.UUID
) -> TrainerClientItem:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer or trainer.gym_id != gym_id:
        raise ResourceNotFoundException("Trainer", trainer_id)

    member = await session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", member_id)

    # End any active assignment for this member
    existing_stmt = select(TrainerMemberAssignment).where(
        TrainerMemberAssignment.gym_id == gym_id,
        TrainerMemberAssignment.member_id == member_id,
        TrainerMemberAssignment.status == "active",
    )
    existing_assignments = (await session.execute(existing_stmt)).scalars().all()
    now = datetime.now(timezone.utc)
    for ea in existing_assignments:
        ea.status = "ended"
        ea.ended_at = now

    assignment = TrainerMemberAssignment(
        gym_id=gym_id,
        trainer_id=trainer_id,
        member_id=member_id,
        assigned_at=now,
        status="active",
    )
    session.add(assignment)
    member.trainer_id = trainer_id

    await session.commit()
    await session.refresh(assignment)

    m_stmt = (
        select(Membership, MembershipPlan)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(Membership.member_id == member.id)
        .order_by(Membership.created_at.desc())
        .limit(1)
    )
    m_row = (await session.execute(m_stmt)).first()

    return TrainerClientItem(
        id=assignment.id,
        member_id=member.id,
        name=member.name,
        email=member.email,
        phone=member.phone,
        age=member.age,
        gender=member.gender,
        membership_plan_name=m_row[1].name if m_row else None,
        membership_status=m_row[0].status if m_row else None,
        membership_end_date=m_row[0].end_date if m_row else None,
        assigned_at=assignment.assigned_at,
        status="active",
    )


async def unassign_trainer_client(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID, member_id: uuid.UUID
) -> None:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer or trainer.gym_id != gym_id:
        raise ResourceNotFoundException("Trainer", trainer_id)

    member = await session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", member_id)

    stmt = select(TrainerMemberAssignment).where(
        TrainerMemberAssignment.gym_id == gym_id,
        TrainerMemberAssignment.trainer_id == trainer_id,
        TrainerMemberAssignment.member_id == member_id,
        TrainerMemberAssignment.status == "active",
    )
    active_assignments = (await session.execute(stmt)).scalars().all()
    now = datetime.now(timezone.utc)
    for a in active_assignments:
        a.status = "ended"
        a.ended_at = now

    if member.trainer_id == trainer_id:
        member.trainer_id = None

    await session.commit()


# ============================================================
# Trainer Reviews Management
# ============================================================

async def list_trainer_reviews(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID
) -> TrainerReviewListResponse:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer or trainer.gym_id != gym_id:
        raise ResourceNotFoundException("Trainer", trainer_id)

    stmt = (
        select(TrainerReview, Member)
        .join(Member, TrainerReview.member_id == Member.id)
        .where(TrainerReview.gym_id == gym_id, TrainerReview.trainer_id == trainer_id)
        .order_by(TrainerReview.created_at.desc())
    )
    rows = (await session.execute(stmt)).all()
    items = [
        TrainerReviewResponse(
            id=r[0].id,
            trainer_id=r[0].trainer_id,
            member_id=r[0].member_id,
            member_name=r[1].name if r[1] else "Gym Member",
            rating=r[0].rating,
            review=r[0].review,
            created_at=r[0].created_at,
        )
        for r in rows
    ]
    avg_r = round(sum(i.rating for i in items) / len(items), 1) if items else None
    return TrainerReviewListResponse(items=items, total=len(items), average_rating=avg_r)


async def create_trainer_review(
    session: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID, data: TrainerReviewCreate
) -> TrainerReviewResponse:
    trainer = await session.get(Trainer, trainer_id)
    if not trainer or trainer.gym_id != gym_id:
        raise ResourceNotFoundException("Trainer", trainer_id)

    member = await session.get(Member, data.member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", data.member_id)

    rev = TrainerReview(
        gym_id=gym_id,
        trainer_id=trainer_id,
        member_id=data.member_id,
        rating=data.rating,
        review=data.review,
    )
    session.add(rev)
    await session.commit()
    await session.refresh(rev)

    return TrainerReviewResponse(
        id=rev.id,
        trainer_id=rev.trainer_id,
        member_id=rev.member_id,
        member_name=member.name,
        rating=rev.rating,
        review=rev.review,
        created_at=rev.created_at,
    )
