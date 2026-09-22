import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.trainer import Trainer
from app.models.member import Member
from app.models.payment import Payment
from app.schemas.trainer import TrainerCreate, TrainerUpdate, TrainerResponse, TrainerListResponse
from app.core.exceptions import ResourceNotFoundException, TenantAccessDeniedException


async def _enrich_trainer(session: AsyncSession, t: Trainer) -> TrainerResponse:
    # Count assigned members
    m_count_stmt = select(func.count(Member.id)).where(
        Member.gym_id == t.gym_id,
        Member.trainer_id == t.id,
    )
    assigned_count = (await session.execute(m_count_stmt)).scalar() or 0

    # Revenue from assigned members
    rev_stmt = (
        select(func.sum(Payment.amount))
        .join(Member, Payment.member_id == Member.id)
        .where(
            Payment.gym_id == t.gym_id,
            Member.trainer_id == t.id,
            Payment.status == "paid",
        )
    )
    revenue = float((await session.execute(rev_stmt)).scalar() or 0.0)

    load_pct = round((assigned_count / t.max_client_capacity * 100.0), 1) if t.max_client_capacity > 0 else 0.0
    retention = round(85.0 + (t.rating - 4.5) * 15.0, 1) if t.rating >= 4.0 else 75.0

    return TrainerResponse(
        id=t.id,
        gym_id=t.gym_id,
        user_id=t.user_id,
        name=t.name,
        email=t.email,
        phone=t.phone,
        specialty=t.specialty,
        years_of_experience=t.years_of_experience,
        certification=t.certification,
        certification_level=t.certification_level,
        joining_date=t.joining_date,
        employment_type=t.employment_type,
        status=t.status,
        max_client_capacity=t.max_client_capacity,
        rating=t.rating,
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
        years_of_experience=data.years_of_experience,
        certification=data.certification,
        certification_level=data.certification_level,
        joining_date=data.joining_date,
        employment_type=data.employment_type,
        status=data.status,
        max_client_capacity=data.max_client_capacity,
        rating=data.rating,
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

    for field, val in data.model_dump(exclude_unset=True).items():
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
