"""assignments_reviews_and_plan_enhancements

Revision ID: 005_assignments_reviews_and_plan_enhancements
Revises: 004_expanded_bi_models
Create Date: 2026-09-23 00:30:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa

revision: str = '005_assignments_reviews_and_plan_enhancements'
down_revision: Union[str, None] = '004_expanded_bi_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    inspector = sa.inspect(bind)

    # 1. Add description and status to membership_plans if not present
    existing_plan_cols = [c['name'] for c in inspector.get_columns('membership_plans')]
    if 'description' not in existing_plan_cols:
        op.add_column('membership_plans', sa.Column('description', sa.String(length=500), nullable=True))
    if 'status' not in existing_plan_cols:
        op.add_column('membership_plans', sa.Column('status', sa.String(length=50), nullable=False, server_default='active'))

    # 2. Add bio to trainers if not present
    existing_trainer_cols = [c['name'] for c in inspector.get_columns('trainers')]
    if 'bio' not in existing_trainer_cols:
        op.add_column('trainers', sa.Column('bio', sa.String(length=1000), nullable=True))

    # 3. Create trainer_member_assignments table if not present
    existing_tables = inspector.get_table_names()
    if 'trainer_member_assignments' not in existing_tables:
        op.create_table(
            'trainer_member_assignments',
            sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('gym_id', sa.Uuid(as_uuid=True), sa.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('trainer_id', sa.Uuid(as_uuid=True), sa.ForeignKey('trainers.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('member_id', sa.Uuid(as_uuid=True), sa.ForeignKey('members.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index('ix_trainer_assignments_gym_trainer', 'trainer_member_assignments', ['gym_id', 'trainer_id', 'status'])
        op.create_index('ix_trainer_assignments_gym_member', 'trainer_member_assignments', ['gym_id', 'member_id', 'status'])

    # 4. Create trainer_reviews table if not present
    if 'trainer_reviews' not in existing_tables:
        op.create_table(
            'trainer_reviews',
            sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('gym_id', sa.Uuid(as_uuid=True), sa.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('trainer_id', sa.Uuid(as_uuid=True), sa.ForeignKey('trainers.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('member_id', sa.Uuid(as_uuid=True), sa.ForeignKey('members.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('review', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index('ix_trainer_reviews_gym_trainer', 'trainer_reviews', ['gym_id', 'trainer_id'])
        op.create_index('ix_trainer_reviews_trainer_id', 'trainer_reviews', ['trainer_id'])

    # 5. RLS policies for PostgreSQL
    if dialect_name == 'postgresql':
        for table in ['trainer_member_assignments', 'trainer_reviews']:
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
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

    # 6. Data-repair: Ensure all existing gyms have default membership plans
    conn = op.get_bind()
    gyms = conn.execute(sa.text("SELECT id FROM gyms")).fetchall()
    now = datetime.now(timezone.utc)
    for (g_id,) in gyms:
        # Check plan count
        p_count = conn.execute(
            sa.text("SELECT count(*) FROM membership_plans WHERE gym_id = :gid"),
            {"gid": g_id}
        ).scalar()
        if p_count == 0:
            default_plans = [
                ("Power Monthly", "Full facility and equipment access, monthly billing", 1800.0, 30),
                ("Power Quarterly", "Full facility access with quarterly savings", 4500.0, 90),
                ("Premium Annual", "Full VIP facility access with yearly savings", 15000.0, 365),
            ]
            for pname, pdesc, pprice, pdur in default_plans:
                plan_uuid = uuid.uuid4().hex if dialect_name == 'sqlite' else uuid.uuid4()
                conn.execute(
                    sa.text("""
                        INSERT INTO membership_plans (id, gym_id, name, description, price, duration_days, status, created_at)
                        VALUES (:id, :gid, :name, :desc, :price, :dur, 'active', :cat)
                    """),
                    {
                        "id": plan_uuid,
                        "gid": g_id,
                        "name": pname,
                        "desc": pdesc,
                        "price": pprice,
                        "dur": pdur,
                        "cat": now,
                    }
                )


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    if dialect_name == 'postgresql':
        op.execute("DROP POLICY IF EXISTS tenant_isolation_trainer_reviews_policy ON trainer_reviews;")
        op.execute("DROP POLICY IF EXISTS tenant_isolation_trainer_member_assignments_policy ON trainer_member_assignments;")
    op.drop_table('trainer_reviews')
    op.drop_table('trainer_member_assignments')
    op.drop_column('trainers', 'bio')
    op.drop_column('membership_plans', 'status')
    op.drop_column('membership_plans', 'description')
