import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberListResponse
from app.services.member_service import (
    list_members,
    get_member,
    create_member,
    update_member,
    delete_member,
)

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=MemberListResponse)
async def get_members(
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_members(
        db, gym_id=current_user.gym_id, search=search, status=status, page=page, size=size
    )


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    data: MemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_member(db, gym_id=current_user.gym_id, data=data)


@router.get("/{member_id}", response_model=MemberResponse)
async def retrieve_member(
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_member(db, gym_id=current_user.gym_id, member_id=member_id)


@router.patch("/{member_id}", response_model=MemberResponse)
async def edit_member(
    member_id: uuid.UUID,
    data: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_member(
        db, gym_id=current_user.gym_id, member_id=member_id, data=data
    )


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_member(db, gym_id=current_user.gym_id, member_id=member_id)
