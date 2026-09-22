import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.trainer import TrainerCreate, TrainerUpdate, TrainerResponse, TrainerListResponse
from app.services.trainer_service import (
    list_trainers,
    get_trainer,
    create_trainer,
    update_trainer,
    delete_trainer,
)

router = APIRouter(prefix="/trainers", tags=["Trainers"])


@router.get("", response_model=TrainerListResponse)
async def get_trainers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_trainers(db, gym_id=current_user.gym_id)


@router.get("/{trainer_id}", response_model=TrainerResponse)
async def retrieve_trainer(
    trainer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_trainer(db, gym_id=current_user.gym_id, trainer_id=trainer_id)


@router.post("", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
async def add_trainer(
    data: TrainerCreate,
    current_user: User = Depends(require_role(["owner", "staff"])),
    db: AsyncSession = Depends(get_db),
):
    return await create_trainer(db, gym_id=current_user.gym_id, data=data)


@router.patch("/{trainer_id}", response_model=TrainerResponse)
async def edit_trainer(
    trainer_id: uuid.UUID,
    data: TrainerUpdate,
    current_user: User = Depends(require_role(["owner", "staff"])),
    db: AsyncSession = Depends(get_db),
):
    return await update_trainer(
        db, gym_id=current_user.gym_id, trainer_id=trainer_id, data=data
    )


@router.delete("/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_trainer(
    trainer_id: uuid.UUID,
    current_user: User = Depends(require_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    await delete_trainer(db, gym_id=current_user.gym_id, trainer_id=trainer_id)
