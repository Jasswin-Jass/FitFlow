from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.payment_service import handle_payment_webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/payment")
async def payment_gateway_webhook(
    request: Request,
    provider: str = Query("demo", description="Gateway provider identifier, e.g. demo, razorpay"),
    db: AsyncSession = Depends(get_db),
):
    """
    Generic webhook receiver for payment gateways.
    Guarantees event idempotency and updates transaction and subscription records accordingly.
    """
    payload = await request.json()
    headers = dict(request.headers)
    return await handle_payment_webhook(
        session=db,
        provider_name=provider,
        payload=payload,
        headers=headers,
    )
