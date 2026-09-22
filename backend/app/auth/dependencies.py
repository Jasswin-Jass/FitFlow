from typing import List, Optional
import uuid
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db, set_tenant_context
from app.models.user import User
from app.models.gym import Gym
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationFailedException,
    AuthorizationFailedException,
    TenantAccessDeniedException,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise AuthenticationFailedException("Authentication token required")

    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationFailedException("Invalid or expired authentication token")

    user_id_str = payload.get("sub")
    gym_id_str = payload.get("gym_id")

    if not user_id_str or not gym_id_str:
        raise AuthenticationFailedException("Token payload missing tenant identity claims")

    try:
        user_id = uuid.UUID(user_id_str)
        gym_id = uuid.UUID(gym_id_str)
    except ValueError:
        raise AuthenticationFailedException("Malformed identifier in authentication token")

    # Retrieve user
    user = await session.get(User, user_id)
    if not user or user.gym_id != gym_id:
        raise AuthenticationFailedException("User not found or gym mismatch")

    # Set PostgreSQL RLS context for database-level tenant isolation
    await set_tenant_context(session, user.gym_id)

    return user


def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationFailedException(
                f"Role '{current_user.role}' not permitted. Requires one of: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


# Shortcuts
get_current_owner = require_role(["owner"])
get_current_staff = require_role(["owner", "staff"])
get_any_gym_user = require_role(["owner", "trainer", "staff"])
