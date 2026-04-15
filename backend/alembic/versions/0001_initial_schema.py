"""
Initial schema for Nivo backend.

Creates all core tables: users, wallets, transactions, PQC keys, etc.

Revision ID: 0001
Revises:
Create Date: 2026-04-14 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables."""

    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone_number", sa.String(15), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("plan", sa.Enum("free", "plus", "pro", name="userplanenum"), nullable=False, server_default="free"),
        sa.Column("kyc_status", sa.Enum("pending", "verified", "rejected", name="kycstatusenum"), nullable=False, server_default="pending"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number", name="uq_user_phone"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )
    op.create_index("ix_users_phone_number", "users", ["phone_number"])

    # wallets table
    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="COP"),
        sa.Column("display_balance_cop", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("custody_mode", sa.Enum("visual_only", "partner_ledger", "sedpe", "bank_partner", name="custodymodeenum"), nullable=False, server_default="visual_only"),
        sa.Column("provider_account_ref", sa.String(120), nullable=True),
        sa.Column("is_frozen", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_wallet_user"),
        sa.CheckConstraint("display_balance_cop >= 0", name="ck_wallet_balance_nonnegative"),
    )

    # savings_pockets table
    op.create_table(
        "savings_pockets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("target_amount_cop", sa.BigInteger(), nullable=True),
        sa.Column("display_balance_cop", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("provider_subaccount_ref", sa.String(120), nullable=True),
        sa.Column("mode", sa.Enum("visual_goal", "partner_subaccount", "custodial", name="savingsmodeenum"), nullable=False, server_default="visual_goal"),
        sa.Column("ml_dsa_last_state_signature", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_savings_pockets_user_id", "savings_pockets", ["user_id"])

    # pqc_keys table
    op.create_table(
        "pqc_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("algorithm", sa.String(30), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("key_fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("key_fingerprint", name="uq_pqc_key_fingerprint"),
    )
    op.create_index("ix_pqc_keys_user_id", "pqc_keys", ["user_id"])
    op.create_index("ix_pqc_keys_key_fingerprint", "pqc_keys", ["key_fingerprint"])
    op.create_index("idx_user_algo_active", "pqc_keys", ["user_id", "algorithm", "is_active"])

    # transactions table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receiver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cop", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.Enum("pending", "pending_confirmation", "completed", "failed", "reversed", name="transactionstatusenum"), nullable=False, server_default="pending"),
        sa.Column("ml_dsa_signature", sa.LargeBinary(), nullable=False),
        sa.Column("signature_key_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rail", sa.Enum("pse", "ach", "bank_partner", "internal", name="settlementrailenum"), nullable=False, server_default="internal"),
        sa.Column("provider_reference", sa.String(120), nullable=True),
        sa.Column("settlement_status", sa.Enum("pending", "settled", "failed", "reversed", name="settlementstatusenum"), nullable=False, server_default="pending"),
        sa.Column("message", sa.String(500), nullable=True),
        sa.Column("metadata_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["signature_key_id"], ["pqc_keys.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount_cop > 0", name="ck_transaction_amount_positive"),
    )
    op.create_index("ix_transactions_sender_id", "transactions", ["sender_id"])
    op.create_index("ix_transactions_receiver_id", "transactions", ["receiver_id"])
    op.create_index("ix_transactions_status", "transactions", ["status"])
    op.create_index("idx_sender_created", "transactions", ["sender_id", "created_at"])
    op.create_index("idx_receiver_created", "transactions", ["receiver_id", "created_at"])

    # otps table
    op.create_table(
        "otps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone_number", sa.String(15), nullable=False),
        sa.Column("otp_hash", sa.String(64), nullable=False),
        sa.Column("purpose", sa.Enum("login", "payment", "kyc", name="otppurposeenum"), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_otps_phone_number", "otps", ["phone_number"])
    op.create_index("idx_phone_expires", "otps", ["phone_number", "expires_at"])

    # merchants table
    op.create_table(
        "merchants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("nit", sa.String(20), nullable=True),
        sa.Column("plan", sa.Enum("basic", "pro", "enterprise", name="merchantplanenum"), nullable=False, server_default="basic"),
        sa.Column("qr_code_signature", sa.LargeBinary(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("nit", name="uq_merchant_nit"),
    )
    op.create_index("ix_merchants_owner_id", "merchants", ["owner_id"])

    # product_disclosures table
    op.create_table(
        "product_disclosures",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_type", sa.Enum("fx", "crypto", "stock", "etf", name="producttypeenum"), nullable=False),
        sa.Column("version", sa.String(30), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_type", "version", name="uq_product_version"),
    )

    # partner_orders table
    op.create_table(
        "partner_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_type", sa.Enum("fx", "crypto", "stock", "etf", name="producttypeenum"), nullable=False),
        sa.Column("partner", sa.String(80), nullable=False),
        sa.Column("partner_order_id", sa.String(120), nullable=True),
        sa.Column("instrument_symbol", sa.String(30), nullable=False),
        sa.Column("side", sa.Enum("buy", "sell", "convert", name="sideenum"), nullable=False),
        sa.Column("notional_amount", sa.BigInteger(), nullable=False),
        sa.Column("source_currency", sa.String(10), nullable=False),
        sa.Column("target_currency", sa.String(10), nullable=False),
        sa.Column("execution_status", sa.Enum("pending", "submitted", "executed", "failed", "cancelled", name="executionstatusenum"), nullable=False, server_default="pending"),
        sa.Column("risk_disclosure_version", sa.String(30), nullable=False),
        sa.Column("accepted_disclosure_hash", sa.String(64), nullable=False),
        sa.Column("signed_order_payload", sa.LargeBinary(), nullable=False),
        sa.Column("ml_dsa_signature", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_partner_orders_user_id", "partner_orders", ["user_id"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("partner_orders")
    op.drop_table("product_disclosures")
    op.drop_table("merchants")
    op.drop_table("otps")
    op.drop_table("transactions")
    op.drop_table("pqc_keys")
    op.drop_table("savings_pockets")
    op.drop_table("wallets")
    op.drop_table("users")
