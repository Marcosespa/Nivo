"""Make ml_dsa_signature and signature_key_id nullable for PSE top-up transactions.

PSE top-ups are authenticated by Wompi HMAC, not by a user PQC signature.
Only P2P payments carry a real ML-DSA-65 signature.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("transactions", "ml_dsa_signature", nullable=True)
    op.alter_column("transactions", "signature_key_id", nullable=True)

    # Recrear FK con SET NULL para que al borrar una pqc_key no elimine la transacción
    op.drop_constraint(
        "transactions_signature_key_id_fkey",
        "transactions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "transactions_signature_key_id_fkey",
        "transactions",
        "pqc_keys",
        ["signature_key_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "transactions_signature_key_id_fkey",
        "transactions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "transactions_signature_key_id_fkey",
        "transactions",
        "pqc_keys",
        ["signature_key_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    # NOTA: el downgrade fallará si existen filas con NULL en estos campos
    op.alter_column("transactions", "signature_key_id", nullable=False)
    op.alter_column("transactions", "ml_dsa_signature", nullable=False)
