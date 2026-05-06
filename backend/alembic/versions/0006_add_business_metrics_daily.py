"""Add business_metrics_daily table for T-13.

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_metrics_daily",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("snapshot_date", sa.Date, nullable=False),
        sa.Column("gmv_cop", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("p2p_transactions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("topup_transactions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("p2p_success_rate", sa.Float, nullable=False, server_default="0"),
        sa.Column("new_users", sa.Integer, nullable=False, server_default="0"),
        sa.Column("active_users", sa.Integer, nullable=False, server_default="0"),
        sa.Column("kyc_approved", sa.Integer, nullable=False, server_default="0"),
        sa.Column("kyc_rejected", sa.Integer, nullable=False, server_default="0"),
        sa.Column("otps_generated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("plan_free_users", sa.Integer, nullable=False, server_default="0"),
        sa.Column("plan_plus_users", sa.Integer, nullable=False, server_default="0"),
        sa.Column("plan_pro_users", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "calculated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("snapshot_date", name="uq_business_metrics_date"),
    )
    op.create_index(
        "ix_business_metrics_daily_snapshot_date",
        "business_metrics_daily",
        ["snapshot_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_business_metrics_daily_snapshot_date", "business_metrics_daily"
    )
    op.drop_table("business_metrics_daily")
