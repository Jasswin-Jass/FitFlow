import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.membership_plan import (
    MembershipPlanCreate,
    MembershipPlanUpdate,
    MembershipPlanResponse,
    MembershipPlanListResponse,
)
from app.services.membership_service import (
    list_plans,
    get_plan,
    create_plan,
    update_plan,
    delete_plan,
)

router = APIRouter(prefix="/membership-plans", tags=["Membership Plans"])


@router.get("", response_model=MembershipPlanListResponse)
async def get_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_plans(db, gym_id=current_user.gym_id)


@router.get("/{plan_id}", response_model=MembershipPlanResponse)
async def retrieve_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_plan(db, gym_id=current_user.gym_id, plan_id=plan_id)


@router.post("", response_model=MembershipPlanResponse, status_code=status.HTTP_201_CREATED)
async def add_plan(
    data: MembershipPlanCreate,
    current_user: User = Depends(require_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    return await create_plan(db, gym_id=current_user.gym_id, data=data)


@router.patch("/{plan_id}", response_model=MembershipPlanResponse)
async def edit_plan(
    plan_id: uuid.UUID,
    data: MembershipPlanUpdate,
    current_user: User = Depends(require_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    return await update_plan(db, gym_id=current_user.gym_id, plan_id=plan_id, data=data)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    await delete_plan(db, gym_id=current_user.gym_id, plan_id=plan_id)
