"""initial schema

Revision ID: e5625217c132
Revises: 
Create Date: 2025-09-09 10:26:21.862923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5625217c132'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # Define PostgreSQL ENUM types
    user_role = sa.Enum('owner', 'worker', 'vet', name='user_role')
    pig_sex = sa.Enum('M', 'F', name='pig_sex')
    pig_class = sa.Enum('piglet', 'grower', 'finisher', 'sow', 'boar', name='pig_class')
    pig_status = sa.Enum('active', 'sold', 'dead', name='pig_status')
    breeding_method = sa.Enum('natural', 'ai', name='breeding_method')
    pregnancy_status = sa.Enum('pos', 'neg', 'unknown', name='pregnancy_status')
    task_link_type = sa.Enum('pig', 'litter', name='task_link_type')
    task_status = sa.Enum('open', 'done', name='task_status')
    task_priority = sa.Enum('low', 'med', 'high', name='task_priority')
    file_kind = sa.Enum('photo', 'doc', name='file_kind')

    # Create ENUM types explicitly to ensure presence before usage
    for enum_type in (
        user_role,
        pig_sex,
        pig_class,
        pig_status,
        breeding_method,
        pregnancy_status,
        task_link_type,
        task_status,
        task_priority,
        file_kind,
    ):
        enum_type.create(bind, checkfirst=True)

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), nullable=True, unique=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('role', user_role, nullable=True),
        sa.Column('password_hash', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Pigs table
    op.create_table(
        'pigs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ear_tag', sa.Text(), nullable=False),
        sa.Column('sex', pig_sex, nullable=True),
        sa.Column('breed', sa.Text(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('class', pig_class, nullable=True),
        sa.Column('source', sa.Text(), nullable=True),
        sa.Column('status', pig_status, server_default=sa.text("'active'::pig_status"), nullable=False),
        sa.Column('current_pen', sa.Text(), nullable=True),
        sa.Column('sire_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('dam_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint('ear_tag', name='uq_pigs_ear_tag'),
    )

    # WeightRecords table
    op.create_table(
        'weight_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Numeric(6, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('weight_kg > 0', name='ck_weight_records_weight_positive'),
    )
    op.create_index('ix_weight_records_pig_date', 'weight_records', ['pig_id', 'date'], unique=False)

    # BreedingEvents table
    op.create_table(
        'breeding_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('service_date', sa.Date(), nullable=True),
        sa.Column('method', breeding_method, server_default=sa.text("'natural'::breeding_method"), nullable=False),
        # expected_farrow computed on server: service_date + 115 days
        sa.Column('expected_farrow', sa.Date(), sa.Computed("(service_date + interval '115 days')::date", persisted=True)),
        sa.Column('preg_check_date', sa.Date(), nullable=True),
        sa.Column('preg_status', pregnancy_status, server_default=sa.text("'unknown'::pregnancy_status"), nullable=False),
        sa.Column('parity', sa.Integer(), nullable=True),
        sa.Column('pen_at_service', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # Litters table
    op.create_table(
        'litters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('farrow_date', sa.Date(), nullable=True),
        sa.Column('liveborn', sa.Integer(), nullable=True),
        sa.Column('stillborn', sa.Integer(), nullable=True),
        sa.Column('neonatal_deaths', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('wean_date', sa.Date(), nullable=True),
        sa.CheckConstraint('liveborn >= 0', name='ck_litters_liveborn_nonneg'),
        sa.CheckConstraint('stillborn >= 0', name='ck_litters_stillborn_nonneg'),
        sa.CheckConstraint('neonatal_deaths >= 0', name='ck_litters_neonatal_nonneg'),
    )

    # HealthEvents table
    op.create_table(
        'health_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('pen', sa.Text(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('product', sa.Text(), nullable=True),
        sa.Column('dose', sa.Text(), nullable=True),
        sa.Column('route', sa.Text(), nullable=True),
        sa.Column('vet_name', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cost', sa.Numeric(10, 2), nullable=True),
        sa.CheckConstraint('cost >= 0', name='ck_health_events_cost_nonneg'),
    )

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('link_type', task_link_type, nullable=True),
        sa.Column('link_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', task_status, server_default=sa.text("'open'::task_status"), nullable=False),
        sa.Column('priority', task_priority, server_default=sa.text("'med'::task_priority"), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Files table
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=True),
        sa.Column('kind', file_kind, nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse dependency order
    op.drop_table('files')
    op.drop_table('tasks')
    op.drop_table('health_events')
    op.drop_table('litters')
    op.drop_table('breeding_events')
    op.drop_index('ix_weight_records_pig_date', table_name='weight_records')
    op.drop_table('weight_records')
    op.drop_table('pigs')
    op.drop_table('users')

    # Drop ENUM types
    bind = op.get_bind()
    for enum_name in (
        'file_kind',
        'task_priority',
        'task_status',
        'task_link_type',
        'pregnancy_status',
        'breeding_method',
        'pig_status',
        'pig_class',
        'pig_sex',
        'user_role',
    ):
        sa.Enum(name=enum_name).drop(bind, checkfirst=True)
