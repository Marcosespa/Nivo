"""
Add bank_accounts table for ACH withdrawals (TASK-008).

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-06 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enum compartido con app.models.orm.bank_account.AccountTypeEnum
    account_type_enum = sa.Enum(
        "savings",
        "checking",
        name="accounttypeenum",
    )

    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bank_code", sa.String(length=10), nullable=False),
        sa.Column("account_type", account_type_enum, nullable=False),
        sa.Column("account_number_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("account_holder_name", sa.String(length=255), nullable=False),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("verification_amount_cop", sa.BigInteger(), nullable=True),
        sa.Column("verification_amount_hash", sa.LargeBinary(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_bank_accounts_user_id",
        "bank_accounts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_user_verified",
        "bank_accounts",
        ["user_id", "is_verified"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_user_verified", table_name="bank_accounts")
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
    sa.Enum(name="accounttypeenum").drop(op.get_bind(), checkfirst=True)
