"""
Nivo — Modelo de Transacción

Cada transacción tiene una firma ML-DSA-65 que la hace
inmutable y verificable a perpetuidad.
"""

from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PENDING_CONFIRMATION = "pending_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class SettlementRail(str, Enum):
    """Canal de liquidación de fondos."""
    PSE = "pse"
    ACH = "ach"
    BANK_PARTNER = "bank_partner"
    INTERNAL = "internal"


class SettlementStatus(str, Enum):
    """Estado de liquidación con el proveedor regulado."""
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"
    REVERSED = "reversed"


class Transaction(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    amount_cop: int              # En centavos
    status: TransactionStatus
    ml_dsa_signature: bytes      # Firma ML-DSA-65 del payload
    signature_key_id: str        # ID de la llave usada para firmar
    message: str | None = None
    rail: SettlementRail = SettlementRail.INTERNAL
    provider_reference: str | None = None
    settlement_status: SettlementStatus = SettlementStatus.PENDING
    created_at: datetime
    confirmed_at: datetime | None = None

    @property
    def amount_display(self) -> str:
        return f"${self.amount_cop / 100:,.0f} COP"
