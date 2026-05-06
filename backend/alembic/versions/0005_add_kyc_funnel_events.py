"""Add kyc_funnel_events table for conversion analytics (T-10).

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kyc_funnel_events",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "step",
            sa.Enum(
                "registered",
                "kyc_initiated",
                "kyc_result",
                "first_deposit",
                name="kycfunnelstepenum",
            ),
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.Enum("completed", "failed", name="kycfunnelresultenum"),
            nullable=True,
        ),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("session_id", sa.String, nullable=True),
        sa.Column("elapsed_seconds", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_kyc_funnel_events_user_id", "kyc_funnel_events", ["user_id"])
    op.create_index("ix_kyc_funnel_events_step", "kyc_funnel_events", ["step"])
    op.create_index("ix_kyc_funnel_events_created_at", "kyc_funnel_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_kyc_funnel_events_created_at", "kyc_funnel_events")
    op.drop_index("ix_kyc_funnel_events_step", "kyc_funnel_events")
    op.drop_index("ix_kyc_funnel_events_user_id", "kyc_funnel_events")
    op.drop_table("kyc_funnel_events")
    op.execute("DROP TYPE IF EXISTS kycfunnelstepenum")
    op.execute("DROP TYPE IF EXISTS kycfunnelresultenum")
