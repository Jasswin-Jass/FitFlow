import uuid
from datetime import datetime, date, timezone
from typing import Optional, Dict, Any
from app.payments.provider import (
    PaymentProvider,
    PaymentResult,
    SubscriptionResult,
    WebhookResult,
)


class DemoPaymentProvider(PaymentProvider):
    """
    Simulated In-Memory / Test Payment Provider for FitFlow.
    Mimics UPI, Credit/Debit Card, and Netbanking workflows with deterministic
    simulation hooks for demonstrations and automated testing.
    """

    @property
    def provider_name(self) -> str:
        return "demo"

    async def create_payment(
        self,
        amount: float,
        currency: str,
        member_id: uuid.UUID,
        membership_id: Optional[uuid.UUID] = None,
        payment_method: Optional[str] = "upi",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        tx_hex = uuid.uuid4().hex[:12]
        provider_payment_id = f"pay_demo_{tx_hex}"
        payment_link = f"fitflow://demo-checkout/{provider_payment_id}"

        return PaymentResult(
            success=True,
            provider_payment_id=provider_payment_id,
            status="pending",
            amount=amount,
            currency=currency or "INR",
            payment_method=payment_method or "upi",
            payment_link=payment_link,
            metadata=metadata or {},
        )

    async def get_payment(self, provider_payment_id: str) -> PaymentResult:
        return PaymentResult(
            success=True,
            provider_payment_id=provider_payment_id,
            status="paid",
            amount=0.0,
            currency="INR",
        )

    async def create_recurring_subscription(
        self,
        amount: float,
        currency: str,
        member_id: uuid.UUID,
        membership_id: uuid.UUID,
        billing_interval: str,
        next_billing_date: date,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionResult:
        sub_hex = uuid.uuid4().hex[:12]
        provider_subscription_id = f"sub_demo_{sub_hex}"

        return SubscriptionResult(
            success=True,
            provider_subscription_id=provider_subscription_id,
            status="active",
            amount=amount,
            currency=currency or "INR",
            billing_interval=billing_interval or "monthly",
            next_billing_date=next_billing_date,
            metadata=metadata or {},
        )

    async def cancel_recurring_subscription(
        self, provider_subscription_id: str
    ) -> bool:
        return True

    async def retry_payment(self, provider_payment_id: str) -> PaymentResult:
        return PaymentResult(
            success=True,
            provider_payment_id=provider_payment_id,
            status="pending",
            amount=0.0,
            currency="INR",
        )

    async def verify_payment(
        self, provider_payment_id: str, signature: Optional[str] = None
    ) -> bool:
        return True

    async def handle_webhook(
        self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> WebhookResult:
        event_id = payload.get("event_id") or f"evt_demo_{uuid.uuid4().hex[:12]}"
        event_type = payload.get("event") or "payment.captured"
        data = payload.get("payload", {}) or payload

        return WebhookResult(
            event_id=event_id,
            event_type=event_type,
            processed=True,
            provider="demo",
            data=data,
        )
