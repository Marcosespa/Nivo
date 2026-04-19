"""
Add b2b_clients table for B2B PQC-as-a-Service API key auth.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "b2b_clients",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("api_key_hash", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("api_key_hash", name="uq_b2b_clients_api_key_hash"),
    )
    op.create_index(
        "ix_b2b_clients_api_key_hash",
        "b2b_clients",
        ["api_key_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_b2b_clients_api_key_hash", table_name="b2b_clients")
    op.drop_table("b2b_clients")
