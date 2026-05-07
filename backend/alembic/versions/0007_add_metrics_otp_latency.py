"""Add OTP and latency columns to business_metrics_daily.

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "business_metrics_daily",
        sa.Column("otps_verified", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "business_metrics_daily",
        sa.Column("otps_failed", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "business_metrics_daily",
        sa.Column("p2p_latency_p50_ms", sa.Float, nullable=True),
    )
    op.add_column(
        "business_metrics_daily",
        sa.Column("p2p_latency_p95_ms", sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("business_metrics_daily", "p2p_latency_p95_ms")
    op.drop_column("business_metrics_daily", "p2p_latency_p50_ms")
    op.drop_column("business_metrics_daily", "otps_failed")
    op.drop_column("business_metrics_daily", "otps_verified")
