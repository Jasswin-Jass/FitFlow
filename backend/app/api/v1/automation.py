from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import (
    AutomationStatusResponse,
    PaymentReminderResponse,
)
from app.services.automation_service import (
    get_automation_status,
    list_reminders,
    generate_due_reminders,
)

router = APIRouter(prefix="/automation", tags=["Billing Automation"])


@router.get("/status", response_model=AutomationStatusResponse)
async def get_billing_automation_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns automated billing rules, reminder status, active mandate metrics, and recent notification logs.
    """
    return await get_automation_status(db, gym_id=current_user.gym_id)


@router.get("/reminders", response_model=List[PaymentReminderResponse])
async def get_automation_reminders(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists recent payment reminders and notification records.
    """
    return await list_reminders(db, gym_id=current_user.gym_id, limit=limit)


@router.post("/trigger-checks")
async def trigger_reminder_evaluation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates membership expiration windows and creates due reminder notices.
    """
    count = await generate_due_reminders(db, gym_id=current_user.gym_id)
    return {"status": "ok", "reminders_generated": count}
