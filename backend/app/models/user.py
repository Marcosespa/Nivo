"""Nivo — Modelo de Usuario."""

from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class UserPlan(str, Enum):
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"


class KYCStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class User(BaseModel):
    id: str
    phone_number: str
    email: str | None = None
    plan: UserPlan = UserPlan.FREE
    kyc_status: KYCStatus = KYCStatus.PENDING
    pqc_key_fingerprint: str | None = None
    created_at: datetime
    is_active: bool = True
