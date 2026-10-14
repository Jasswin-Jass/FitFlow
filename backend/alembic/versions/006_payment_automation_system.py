"""payment_automation_system

Revision ID: 006_payment_automation_system
Revises: 005_assignments_reviews_and_plan_enhancements
Create Date: 2026-09-23 14:15:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa

revision: str = '006_payment_automation_system'
down_revision: Union[str, None] = '005_assignments_reviews_and_plan_enhancements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    inspector = sa.inspect(bind)

    # 1. Extend payments table
    existing_payment_cols = [c['name'] for c in inspector.get_columns('payments')]
    
    with op.batch_alter_table('payments') as batch_op:
        if 'currency' not in existing_payment_cols:
            batch_op.add_column(sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'))
        if 'payment_method' not in existing_payment_cols:
            batch_op.add_column(sa.Column('payment_method', sa.String(length=50), nullable=True, server_default='upi'))
        if 'provider' not in existing_payment_cols:
            batch_op.add_column(sa.Column('provider', sa.String(length=50), nullable=False, server_default='demo'))
        if 'provider_payment_id' not in existing_payment_cols:
            batch_op.add_column(sa.Column('provider_payment_id', sa.String(length=255), nullable=True))
        if 'payment_link_id' not in existing_payment_cols:
            batch_op.add_column(sa.Column('payment_link_id', sa.String(length=255), nullable=True))
        if 'due_date' not in existing_payment_cols:
            batch_op.add_column(sa.Column('due_date', sa.Date(), nullable=True))
        if 'failure_reason' not in existing_payment_cols:
            batch_op.add_column(sa.Column('failure_reason', sa.String(length=500), nullable=True))
        if 'created_at' not in existing_payment_cols:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
        if 'updated_at' not in existing_payment_cols:
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Add indexes on payments if not exists
    existing_payment_indexes = [ix['name'] for ix in inspector.get_indexes('payments')]
    if 'ix_payments_provider_id' not in existing_payment_indexes:
        op.create_index('ix_payments_provider_id', 'payments', ['provider_payment_id'])
    if 'ix_payments_due_date' not in existing_payment_indexes:
        op.create_index('ix_payments_due_date', 'payments', ['gym_id', 'status', 'due_date'])

    # 2. Create payment_subscriptions table
    existing_tables = inspector.get_table_names()
    if 'payment_subscriptions' not in existing_tables:
        op.create_table(
            'payment_subscriptions',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('gym_id', sa.Uuid(), nullable=False),
            sa.Column('member_id', sa.Uuid(), nullable=False),
            sa.Column('membership_id', sa.Uuid(), nullable=False),
            sa.Column('provider', sa.String(length=50), nullable=False, server_default='demo'),
            sa.Column('provider_subscription_id', sa.String(length=255), nullable=True),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
            sa.Column('billing_interval', sa.String(length=50), nullable=False, server_default='monthly'),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('next_billing_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_subscriptions_gym_status', 'payment_subscriptions', ['gym_id', 'status'])
        op.create_index('ix_subscriptions_due', 'payment_subscriptions', ['gym_id', 'status', 'next_billing_date'])
        op.create_index('ix_subscriptions_member', 'payment_subscriptions', ['member_id', 'status'])

    # 3. Create payment_webhook_events table
    if 'payment_webhook_events' not in existing_tables:
        op.create_table(
            'payment_webhook_events',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('gym_id', sa.Uuid(), nullable=True),
            sa.Column('provider', sa.String(length=50), nullable=False),
            sa.Column('provider_event_id', sa.String(length=255), nullable=False),
            sa.Column('event_type', sa.String(length=100), nullable=False),
            sa.Column('payload', sa.JSON(), nullable=False),
            sa.Column('processed', sa.Boolean(), nullable=False, server_default=sa.text('0' if dialect_name == 'sqlite' else 'false')),
            sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('provider_event_id', name='uq_payment_webhook_event_id'),
        )
        op.create_index('ix_webhook_provider_event', 'payment_webhook_events', ['provider', 'provider_event_id'])

    # 4. Create payment_reminders table
    if 'payment_reminders' not in existing_tables:
        op.create_table(
            'payment_reminders',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('gym_id', sa.Uuid(), nullable=False),
            sa.Column('member_id', sa.Uuid(), nullable=False),
            sa.Column('payment_id', sa.Uuid(), nullable=True),
            sa.Column('reminder_type', sa.String(length=50), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('message', sa.String(length=1000), nullable=False),
            sa.Column('channel', sa.String(length=50), nullable=False, server_default='in_app'),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='sent'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_reminders_gym_member', 'payment_reminders', ['gym_id', 'member_id', 'reminder_type'])
        op.create_index('ix_reminders_created', 'payment_reminders', ['gym_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('payment_reminders')
    op.drop_table('payment_webhook_events')
    op.drop_table('payment_subscriptions')
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('failure_reason')
        batch_op.drop_column('due_date')
        batch_op.drop_column('payment_link_id')
        batch_op.drop_column('provider_payment_id')
        batch_op.drop_column('provider')
        batch_op.drop_column('payment_method')
        batch_op.drop_column('currency')
