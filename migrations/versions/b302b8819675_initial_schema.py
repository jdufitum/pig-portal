"""initial schema

Revision ID: b302b8819675
Revises: 
Create Date: 2025-09-09 10:47:12.871572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql


# revision identifiers, used by Alembic.
revision: str = 'b302b8819675'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ----- Enums -----
    user_role = sa.Enum('owner', 'worker', 'vet', name='user_role', create_type=True)
    pig_sex = sa.Enum('M', 'F', name='pig_sex', create_type=True)
    pig_class = sa.Enum('piglet', 'grower', 'finisher', 'sow', 'boar', name='pig_class', create_type=True)
    pig_status = sa.Enum('active', 'sold', 'dead', name='pig_status', create_type=True)
    breeding_method = sa.Enum('natural', 'ai', name='breeding_method', create_type=True)
    preg_status = sa.Enum('pos', 'neg', 'unknown', name='preg_status', create_type=True)
    task_link_type = sa.Enum('pig', 'litter', name='task_link_type', create_type=True)
    task_status = sa.Enum('open', 'done', name='task_status', create_type=True)
    task_priority = sa.Enum('low', 'med', 'high', name='task_priority', create_type=True)
    file_kind = sa.Enum('photo', 'doc', name='file_kind', create_type=True)

    # Create the enum types explicitly to ensure availability before table creation
    user_role.create(op.get_bind(), checkfirst=True)
    pig_sex.create(op.get_bind(), checkfirst=True)
    pig_class.create(op.get_bind(), checkfirst=True)
    pig_status.create(op.get_bind(), checkfirst=True)
    breeding_method.create(op.get_bind(), checkfirst=True)
    preg_status.create(op.get_bind(), checkfirst=True)
    task_link_type.create(op.get_bind(), checkfirst=True)
    task_status.create(op.get_bind(), checkfirst=True)
    task_priority.create(op.get_bind(), checkfirst=True)
    file_kind.create(op.get_bind(), checkfirst=True)

    # ----- Users -----
    op.create_table(
        'users',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), nullable=False, unique=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('role', user_role, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # ----- Pigs -----
    op.create_table(
        'pigs',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ear_tag', sa.Text(), nullable=False, unique=True),
        sa.Column('sex', pig_sex, nullable=True),
        sa.Column('breed', sa.Text(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('class', pig_class, nullable=True),
        sa.Column('source', sa.Text(), nullable=True),
        sa.Column('status', pig_status, nullable=False, server_default=sa.text("'active'")),
        sa.Column('current_pen', sa.Text(), nullable=True),
        sa.Column('sire_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete=None), nullable=True),
        sa.Column('dam_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete=None), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # ----- WeightRecords -----
    op.create_table(
        'weight_records',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Numeric(6, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('weight_kg > 0', name='ck_weight_records_weight_positive'),
    )
    op.create_index('ix_weight_records_pig_date', 'weight_records', ['pig_id', 'date'], unique=False)

    # ----- BreedingEvents -----
    op.create_table(
        'breeding_events',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('service_date', sa.Date(), nullable=True),
        sa.Column('method', breeding_method, nullable=False, server_default=sa.text("'natural'")),
        sa.Column('expected_farrow', sa.Date(), sa.Computed("(service_date + INTERVAL '115 days')::date", persisted=True), nullable=True),
        sa.Column('preg_check_date', sa.Date(), nullable=True),
        sa.Column('preg_status', preg_status, nullable=False, server_default=sa.text("'unknown'")),
        sa.Column('parity', sa.Integer(), nullable=True),
        sa.Column('pen_at_service', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # ----- Litters -----
    op.create_table(
        'litters',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('farrow_date', sa.Date(), nullable=True),
        sa.Column('liveborn', sa.Integer(), nullable=True),
        sa.Column('stillborn', sa.Integer(), nullable=True),
        sa.Column('neonatal_deaths', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('wean_date', sa.Date(), nullable=True),
        sa.CheckConstraint('liveborn IS NULL OR liveborn >= 0', name='ck_litters_liveborn_nonneg'),
        sa.CheckConstraint('stillborn IS NULL OR stillborn >= 0', name='ck_litters_stillborn_nonneg'),
        sa.CheckConstraint('neonatal_deaths >= 0', name='ck_litters_neonatal_deaths_nonneg'),
    )

    # ----- HealthEvents -----
    op.create_table(
        'health_events',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('pen', sa.Text(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('product', sa.Text(), nullable=True),
        sa.Column('dose', sa.Text(), nullable=True),
        sa.Column('route', sa.Text(), nullable=True),
        sa.Column('vet_name', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cost', sa.Numeric(10, 2), nullable=True),
        sa.CheckConstraint('cost IS NULL OR cost >= 0', name='ck_health_events_cost_nonneg'),
    )

    # ----- Tasks -----
    op.create_table(
        'tasks',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('assigned_to', psql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('link_type', task_link_type, nullable=True),
        sa.Column('link_id', psql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', task_status, nullable=False, server_default=sa.text("'open'")),
        sa.Column('priority', task_priority, nullable=False, server_default=sa.text("'med'")),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # ----- Files -----
    op.create_table(
        'files',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', file_kind, nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
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

    # Drop enums
    bind = op.get_bind()
    for enum_name in [
        'file_kind',
        'task_priority',
        'task_status',
        'task_link_type',
        'preg_status',
        'breeding_method',
        'pig_status',
        'pig_class',
        'pig_sex',
        'user_role',
    ]:
        sa.Enum(name=enum_name).drop(bind, checkfirst=True)
