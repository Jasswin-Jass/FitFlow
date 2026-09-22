from typing import AsyncGenerator, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from app.core.config import settings

# Configure async engine
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def set_tenant_context(session: AsyncSession, gym_id: Optional[uuid.UUID]) -> None:
    """
    Sets PostgreSQL session local variable for Row-Level Security (RLS).
    In PostgreSQL, this enforces tenant isolation at the database level.
    """
    if gym_id and engine.dialect.name == "postgresql":
        await session.execute(
            text("SET LOCAL app.current_gym_id = :gym_id"),
            {"gym_id": str(gym_id)},
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Base database session dependency for routes without authenticated tenant context."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
