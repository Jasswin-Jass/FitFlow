import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.membership import (
    MembershipCreate,
    MembershipRenew,
    MembershipUpdate,
    MembershipResponse,
    MembershipListResponse,
)
from app.services.membership_service import (
    list_memberships,
    create_membership,
    renew_membership,
    update_membership,
)

router = APIRouter(prefix="/memberships", tags=["Memberships"])


@router.get("", response_model=MembershipListResponse)
async def get_memberships(
    status: Optional[str] = Query(None, description="Filter by status: active, expired, cancelled"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_memberships(db, gym_id=current_user.gym_id, status=status)


@router.post("", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_membership(
    data: MembershipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_membership(db, gym_id=current_user.gym_id, data=data)


@router.post("/{membership_id}/renew", response_model=MembershipResponse)
async def renew_existing_membership(
    membership_id: uuid.UUID,
    data: MembershipRenew,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await renew_membership(
        db, gym_id=current_user.gym_id, membership_id=membership_id, data=data
    )


@router.patch("/{membership_id}", response_model=MembershipResponse)
async def edit_membership(
    membership_id: uuid.UUID,
    data: MembershipUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_membership(
        db, gym_id=current_user.gym_id, membership_id=membership_id, data=data
    )
