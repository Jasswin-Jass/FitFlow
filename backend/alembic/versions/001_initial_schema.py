"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-22 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. gyms
    op.create_table(
        'gyms',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. users
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_gym_id', 'users', ['gym_id'])
    op.create_index('ix_users_gym_role', 'users', ['gym_id', 'role'])

    # 3. members
    op.create_table(
        'members',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('join_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_members_gym_id', 'members', ['gym_id'])
    op.create_index('ix_members_gym_status', 'members', ['gym_id', 'status'])
    op.create_index('ix_members_gym_name', 'members', ['gym_id', 'name'])

    # 4. trainers
    op.create_table(
        'trainers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('specialty', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trainers_gym_id', 'trainers', ['gym_id'])
    op.create_index('ix_trainers_gym_specialty', 'trainers', ['gym_id', 'specialty'])

    # 5. membership_plans
    op.create_table(
        'membership_plans',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_membership_plans_gym_id', 'membership_plans', ['gym_id'])
    op.create_index('ix_membership_plans_gym_name', 'membership_plans', ['gym_id', 'name'])

    # 6. memberships
    op.create_table(
        'memberships',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('plan_id', sa.Uuid(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['membership_plans.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_memberships_gym_status_dates', 'memberships', ['gym_id', 'status', 'start_date', 'end_date'])
    op.create_index('ix_memberships_member_status', 'memberships', ['member_id', 'status'])

    # 7. payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('membership_id', sa.Uuid(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payments_gym_status_date', 'payments', ['gym_id', 'status', 'paid_at'])
    op.create_index('ix_payments_member_status', 'payments', ['member_id', 'status'])

    # 8. summary_metrics
    op.create_table(
        'summary_metrics',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('active_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mrr', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('renewal_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('at_risk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('churned_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gym_id', 'metric_date', name='uq_summary_metrics_gym_date')
    )
    op.create_index('ix_summary_metrics_gym_date', 'summary_metrics', ['gym_id', 'metric_date'])


def downgrade() -> None:
    op.drop_table('summary_metrics')
    op.drop_table('payments')
    op.drop_table('memberships')
    op.drop_table('membership_plans')
    op.drop_table('trainers')
    op.drop_table('members')
    op.drop_table('users')
    op.drop_table('gyms')
