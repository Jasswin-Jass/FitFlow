from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import require_role
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.analytics.aggregation_service import compute_and_save_daily_metrics, get_dashboard_summary

router = APIRouter(prefix="/admin", tags=["Admin & Aggregation"])


@router.post("/recompute-metrics", response_model=DashboardSummaryResponse)
async def recompute_metrics(
    current_user: User = Depends(require_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually triggers recomputation of metrics for the authenticated owner's gym.
    Updates summary_metrics and returns the freshly updated dashboard values.
    """
    today = date.today()
    await compute_and_save_daily_metrics(db, gym_id=current_user.gym_id, metric_date=today)
    return await get_dashboard_summary(db, gym_id=current_user.gym_id)
