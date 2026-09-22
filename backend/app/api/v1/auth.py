from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import GymRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.auth.service import register_gym_and_owner, authenticate_user
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.gym import Gym

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(req: GymRegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_gym_and_owner(db, req)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, req)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    gym = await db.get(Gym, current_user.gym_id)
    return UserResponse(
        id=current_user.id,
        gym_id=current_user.gym_id,
        gym_name=gym.name if gym else None,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
    )
