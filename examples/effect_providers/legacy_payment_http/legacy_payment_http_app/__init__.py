"""Legacy, module-owned HTTP payment application used by the experiment."""

from .application import PaymentResult, authorize_payment

__all__ = ["PaymentResult", "authorize_payment"]

