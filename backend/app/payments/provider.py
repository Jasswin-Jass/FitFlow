from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import uuid


@dataclass
class PaymentResult:
    success: bool
    provider_payment_id: str
    status: str  # pending, paid, failed, cancelled
    amount: float
    currency: str = "INR"
    payment_method: Optional[str] = "upi"
    payment_link: Optional[str] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionResult:
    success: bool
    provider_subscription_id: str
    status: str  # active, paused, cancelled, past_due, failed
    amount: float
    currency: str = "INR"
    billing_interval: str = "monthly"
    next_billing_date: Optional[date] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookResult:
    event_id: str
    event_type: str
    processed: bool
    provider: str
    data: Dict[str, Any]
    error: Optional[str] = None


class PaymentProvider(ABC):
    """
    Abstract Payment Provider Interface.
    Decouples payment processing logic so real gateways (Razorpay, Stripe, PayU)
    can be plugged in without changing membership, billing, or UI business logic.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier, e.g. 'demo', 'razorpay'."""
        pass

    @abstractmethod
    async def create_payment(
        self,
        amount: float,
        currency: str,
        member_id: uuid.UUID,
        membership_id: Optional[uuid.UUID] = None,
        payment_method: Optional[str] = "upi",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        """Initiates a payment transaction and returns provider reference."""
        pass

    @abstractmethod
    async def get_payment(self, provider_payment_id: str) -> PaymentResult:
        """Retrieves payment state from the provider."""
        pass

    @abstractmethod
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
        """Registers a recurring auto-debit subscription mandate."""
        pass

    @abstractmethod
    async def cancel_recurring_subscription(
        self, provider_subscription_id: str
    ) -> bool:
        """Cancels a recurring payment mandate at the provider."""
        pass

    @abstractmethod
    async def retry_payment(self, provider_payment_id: str) -> PaymentResult:
        """Retries a failed payment."""
        pass

    @abstractmethod
    async def verify_payment(
        self, provider_payment_id: str, signature: Optional[str] = None
    ) -> bool:
        """Verifies payment signature / authenticity."""
        pass

    @abstractmethod
    async def handle_webhook(
        self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> WebhookResult:
        """Processes an incoming asynchronous webhook payload."""
        pass
