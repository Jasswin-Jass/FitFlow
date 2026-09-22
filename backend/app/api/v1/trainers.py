import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.trainer import (
    TrainerCreate,
    TrainerUpdate,
    TrainerResponse,
    TrainerListResponse,
    TrainerClientItem,
    TrainerClientListResponse,
    TrainerClientAssignRequest,
    TrainerReviewCreate,
    TrainerReviewResponse,
    TrainerReviewListResponse,
)
from app.services.trainer_service import (
    list_trainers,
    get_trainer,
    create_trainer,
    update_trainer,
    delete_trainer,
    list_trainer_clients,
    assign_trainer_client,
    unassign_trainer_client,
    list_trainer_reviews,
    create_trainer_review,
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


# ============================================================
# Trainer Clients Endpoints
# ============================================================

@router.get("/{trainer_id}/clients", response_model=TrainerClientListResponse)
async def get_trainer_clients(
    trainer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_trainer_clients(db, gym_id=current_user.gym_id, trainer_id=trainer_id)


@router.post("/{trainer_id}/clients", response_model=TrainerClientItem, status_code=status.HTTP_201_CREATED)
async def assign_client(
    trainer_id: uuid.UUID,
    data: TrainerClientAssignRequest,
    current_user: User = Depends(require_role(["owner", "staff"])),
    db: AsyncSession = Depends(get_db),
):
    return await assign_trainer_client(
        db, gym_id=current_user.gym_id, trainer_id=trainer_id, member_id=data.member_id
    )


@router.delete("/{trainer_id}/clients/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_client(
    trainer_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: User = Depends(require_role(["owner", "staff"])),
    db: AsyncSession = Depends(get_db),
):
    await unassign_trainer_client(
        db, gym_id=current_user.gym_id, trainer_id=trainer_id, member_id=member_id
    )


# ============================================================
# Trainer Reviews Endpoints
# ============================================================

@router.get("/{trainer_id}/reviews", response_model=TrainerReviewListResponse)
async def get_trainer_reviews(
    trainer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_trainer_reviews(db, gym_id=current_user.gym_id, trainer_id=trainer_id)


@router.post("/{trainer_id}/reviews", response_model=TrainerReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_trainer_review(
    trainer_id: uuid.UUID,
    data: TrainerReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_trainer_review(
        db, gym_id=current_user.gym_id, trainer_id=trainer_id, data=data
    )
