"""
Add kyc_provider_id column to users.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing KYC provider reference column to users."""
    op.add_column("users", sa.Column("kyc_provider_id", sa.String(length=120), nullable=True))
    op.create_index("ix_users_kyc_provider_id", "users", ["kyc_provider_id"], unique=False)


def downgrade() -> None:
    """Remove KYC provider reference column from users."""
    op.drop_index("ix_users_kyc_provider_id", table_name="users")
    op.drop_column("users", "kyc_provider_id")
