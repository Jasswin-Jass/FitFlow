"""rls_policies

Revision ID: 002_rls_policies
Revises: 001_initial_schema
Create Date: 2026-09-22 21:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_rls_policies'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TENANT_TABLES = [
    'users',
    'members',
    'trainers',
    'membership_plans',
    'memberships',
    'payments',
    'summary_metrics',
]


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        for table in TENANT_TABLES:
            # Enable Row-Level Security
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
            # Create tenant isolation policy based on session variable app.current_gym_id
            op.execute(
                f"""
                CREATE POLICY tenant_isolation_{table}_policy ON {table}
                FOR ALL
                USING (
                    gym_id = NULLIF(current_setting('app.current_gym_id', true), '')::uuid
                )
                WITH CHECK (
                    gym_id = NULLIF(current_setting('app.current_gym_id', true), '')::uuid
                );
                """
            )


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        for table in TENANT_TABLES:
            op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table}_policy ON {table};")
            op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
