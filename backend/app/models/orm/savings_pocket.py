"""Nivo — Savings Pocket ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SavingsModeEnum(str, Enum):
    """Mode for savings pocket."""
    VISUAL_GOAL = "visual_goal"
    PARTNER_SUBACCOUNT = "partner_subaccount"
    CUSTODIAL = "custodial"


class SavingsPocket(Base):
    """
    Tabla de alcancías — sub-balances visuales que el usuario crea para ahorrar.
    Cada usuario puede tener múltiples alcancías.

    En MVP (visual_goal), es puramente visual — no hay movimiento real de fondos.
    El dinero sigue en la billetera principal.
    """

    __tablename__ = "savings_pockets"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    target_amount_cop: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Meta de ahorro
    display_balance_cop: Mapped[int] = mapped_column(BigInteger, default=0)
    provider_subaccount_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mode: Mapped[SavingsModeEnum] = mapped_column(
        SQLEnum(
            SavingsModeEnum,
            name="savingsmodeenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=SavingsModeEnum.VISUAL_GOAL,
    )
    ml_dsa_last_state_signature: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Relaciones
    user: Mapped[User] = relationship("User", back_populates="savings_pockets")

    def __repr__(self) -> str:
        return f"<SavingsPocket {self.name} balance={self.display_balance_cop}>"


# Import forward reference
from .user import User
