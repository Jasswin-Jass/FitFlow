"""expanded_bi_models

Revision ID: 004_expanded_bi_models
Revises: 002_rls_policies
Create Date: 2026-09-22 23:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_expanded_bi_models'
down_revision: Union[str, None] = '002_rls_policies'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Expand trainers table
    op.add_column('trainers', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('trainers', sa.Column('years_of_experience', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('trainers', sa.Column('certification', sa.String(length=255), nullable=True))
    op.add_column('trainers', sa.Column('certification_level', sa.String(length=100), nullable=True))
    op.add_column('trainers', sa.Column('joining_date', sa.Date(), nullable=True))
    op.add_column('trainers', sa.Column('employment_type', sa.String(length=50), nullable=False, server_default='Full-time'))
    op.add_column('trainers', sa.Column('status', sa.String(length=20), nullable=False, server_default='active'))
    op.add_column('trainers', sa.Column('max_client_capacity', sa.Integer(), nullable=False, server_default='20'))
    op.add_column('trainers', sa.Column('rating', sa.Float(), nullable=False, server_default='5.0'))
    op.create_index('ix_trainers_gym_status', 'trainers', ['gym_id', 'status'])

    # 2. Expand members table
    op.add_column('members', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('members', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('members', sa.Column('occupation', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('emergency_contact_name', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('emergency_contact_phone', sa.String(length=50), nullable=True))
    op.add_column('members', sa.Column('preferred_training_time', sa.String(length=30), nullable=True))
    op.add_column('members', sa.Column('fitness_goal', sa.String(length=50), nullable=True))
    op.add_column('members', sa.Column('acquisition_source', sa.String(length=50), nullable=True))
    op.add_column('members', sa.Column('referral_source', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column('trainer_id', sa.Uuid(), nullable=True))
    
    op.create_foreign_key(
        'fk_members_trainer_id',
        'members', 'trainers',
        ['trainer_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_members_gym_gender', 'members', ['gym_id', 'gender'])
    op.create_index('ix_members_gym_dob', 'members', ['gym_id', 'date_of_birth'])
    op.create_index('ix_members_gym_source', 'members', ['gym_id', 'acquisition_source'])
    op.create_index('ix_members_trainer_id', 'members', ['trainer_id'])

    # 3. summary_metrics renewal_rate nullable
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.alter_column('summary_metrics', 'renewal_rate', nullable=True)


def downgrade() -> None:
    pass
