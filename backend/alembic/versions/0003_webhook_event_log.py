"""Add webhook_event_log table for idempotence.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla webhook_event_logs
    op.create_table(
        'webhook_event_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_event_id', sa.String(length=256), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('raw_payload', sa.String(length=8192), nullable=False),
        # Valores en minúsculas — deben coincidir con WebhookEventStatusEnum (.value) y el ORM
        sa.Column(
            'status',
            sa.Enum(
                'received', 'processing', 'processed', 'failed', 'ignored',
                name='webhookeventstatusenum',
            ),
            nullable=False,
        ),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('error_message', sa.String(length=1024), nullable=True),
        sa.Column('retry_count', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('related_transaction_id', sa.Uuid(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_event_id', name='uc_webhook_provider_event_id'),
    )

    # Crear índices
    op.create_index('idx_webhook_status_received', 'webhook_event_logs', ['status', 'received_at'])
    op.create_index('webhook_event_logs_provider_idx', 'webhook_event_logs', ['provider'])
    op.create_index('webhook_event_logs_status_idx', 'webhook_event_logs', ['status'])
    op.create_index('webhook_event_logs_related_transaction_id_idx', 'webhook_event_logs', ['related_transaction_id'])


def downgrade() -> None:
    op.drop_index('webhook_event_logs_related_transaction_id_idx', table_name='webhook_event_logs')
    op.drop_index('webhook_event_logs_status_idx', table_name='webhook_event_logs')
    op.drop_index('webhook_event_logs_provider_idx', table_name='webhook_event_logs')
    op.drop_index('idx_webhook_status_received', table_name='webhook_event_logs')
    op.drop_table('webhook_event_logs')
