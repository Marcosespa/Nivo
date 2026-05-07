"""Add bank_accounts table for ACH withdrawals.

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bank_accounts",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bank_code", sa.String(10), nullable=False),
        sa.Column(
            "account_type",
            sa.Enum("savings", "checking", name="accounttypeenum"),
            nullable=False,
        ),
        sa.Column("account_number_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("account_holder_name", sa.String(255), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("verification_amount_cop", sa.BigInteger(), nullable=True),
        sa.Column("verification_amount_hash", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_verified", "bank_accounts", ["user_id", "is_verified"])
    op.create_index("ix_bank_accounts_user_id", "bank_accounts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_index("idx_user_verified", table_name="bank_accounts")
    op.drop_table("bank_accounts")
    op.execute("DROP TYPE IF EXISTS accounttypeenum")
