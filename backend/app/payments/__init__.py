from typing import Dict, Type
from app.payments.provider import (
    PaymentProvider,
    PaymentResult,
    SubscriptionResult,
    WebhookResult,
)
from app.payments.demo_provider import DemoPaymentProvider

_PROVIDERS: Dict[str, Type[PaymentProvider]] = {
    "demo": DemoPaymentProvider,
}


def register_payment_provider(name: str, provider_cls: Type[PaymentProvider]):
    """Allows registering future gateways like 'razorpay' dynamically."""
    _PROVIDERS[name.lower()] = provider_cls


def get_payment_provider(name: str = "demo") -> PaymentProvider:
    """
    Factory to retrieve an instance of the configured payment provider.
    Defaults to DemoPaymentProvider.
    """
    key = (name or "demo").lower()
    provider_cls = _PROVIDERS.get(key)
    if not provider_cls:
        raise ValueError(
            f"Unknown payment provider: '{name}'. Available providers: {list(_PROVIDERS.keys())}"
        )
    return provider_cls()


__all__ = [
    "PaymentProvider",
    "PaymentResult",
    "SubscriptionResult",
    "WebhookResult",
    "DemoPaymentProvider",
    "get_payment_provider",
    "register_payment_provider",
]
