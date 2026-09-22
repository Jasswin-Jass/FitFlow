from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.gym import Gym
from app.models.user import User
from app.schemas.auth import GymRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import FitFlowException, AuthenticationFailedException
from app.analytics.aggregation_service import compute_and_save_daily_metrics


async def register_gym_and_owner(
    session: AsyncSession, req: GymRegisterRequest
) -> TokenResponse:
    # Check if user email already exists
    existing = await session.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise FitFlowException(
            status_code=400,
            error="EmailAlreadyExists",
            detail=f"An account with email {req.email} already exists",
        )

    # 1. Create Gym
    gym = Gym(name=req.gym_name)
    session.add(gym)
    await session.flush()

    # 2. Create Owner User
    owner = User(
        gym_id=gym.id,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        role="owner",
    )
    session.add(owner)
    await session.flush()

    # 3. Initialize 0-state summary_metrics for new gym
    await compute_and_save_daily_metrics(session, gym.id)

    await session.commit()
    await session.refresh(gym)
    await session.refresh(owner)

    token = create_access_token(
        subject=str(owner.id),
        gym_id=str(gym.id),
        role=owner.role,
        email=owner.email,
    )

    user_resp = UserResponse(
        id=owner.id,
        gym_id=gym.id,
        gym_name=gym.name,
        email=owner.email,
        role=owner.role,
        created_at=owner.created_at,
    )

    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)


async def authenticate_user(
    session: AsyncSession, req: UserLoginRequest
) -> TokenResponse:
    result = await session.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise AuthenticationFailedException("Invalid email or password")

    gym = await session.get(Gym, user.gym_id)
    gym_name = gym.name if gym else None

    token = create_access_token(
        subject=str(user.id),
        gym_id=str(user.gym_id),
        role=user.role,
        email=user.email,
    )

    user_resp = UserResponse(
        id=user.id,
        gym_id=user.gym_id,
        gym_name=gym_name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )

    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)
