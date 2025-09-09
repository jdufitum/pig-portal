from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    role_enum = psql.ENUM('owner', 'worker', 'vet', name='user_role', create_type=False)
    sex_enum = psql.ENUM('M', 'F', name='pig_sex', create_type=False)
    pig_class_enum = psql.ENUM('piglet','grower','finisher','sow','boar', name='pig_class', create_type=False)
    pig_status_enum = psql.ENUM('active','sold','dead', name='pig_status', create_type=False)
    method_enum = psql.ENUM('natural','ai', name='service_method', create_type=False)
    preg_status_enum = psql.ENUM('pos','neg','unknown', name='preg_status', create_type=False)
    link_type_enum = psql.ENUM('pig','litter', name='task_link_type', create_type=False)
    task_status_enum = psql.ENUM('open','done', name='task_status', create_type=False)
    priority_enum = psql.ENUM('low','med','high', name='task_priority', create_type=False)
    file_kind_enum = psql.ENUM('photo','doc', name='file_kind', create_type=False)

    role_enum.create(op.get_bind(), checkfirst=True)
    sex_enum.create(op.get_bind(), checkfirst=True)
    pig_class_enum.create(op.get_bind(), checkfirst=True)
    pig_status_enum.create(op.get_bind(), checkfirst=True)
    method_enum.create(op.get_bind(), checkfirst=True)
    preg_status_enum.create(op.get_bind(), checkfirst=True)
    link_type_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)
    priority_enum.create(op.get_bind(), checkfirst=True)
    file_kind_enum.create(op.get_bind(), checkfirst=True)

    # Users
    op.create_table(
        'users',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.Text()),
        sa.Column('email', sa.Text(), nullable=False, unique=True),
        sa.Column('phone', sa.Text()),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Pigs
    op.create_table(
        'pigs',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ear_tag', sa.Text(), nullable=False, unique=True),
        sa.Column('sex', sex_enum, nullable=True),
        sa.Column('breed', sa.Text()),
        sa.Column('birth_date', sa.Date()),
        sa.Column('class', pig_class_enum, nullable=True),
        sa.Column('source', sa.Text()),
        sa.Column('status', pig_status_enum, nullable=False, server_default=sa.text("'active'")),
        sa.Column('current_pen', sa.Text()),
        sa.Column('sire_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('dam_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_pigs_ear_tag', 'pigs', ['ear_tag'], unique=True)

    # WeightRecords
    op.create_table(
        'weight_records',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Numeric(6,2), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.CheckConstraint('weight_kg > 0', name='ck_weight_records_weight_positive'),
    )
    op.create_index('ix_weight_records_pig_date', 'weight_records', ['pig_id','date'], unique=False)

    # BreedingEvents
    op.create_table(
        'breeding_events',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('service_date', sa.Date()),
        sa.Column('method', method_enum, nullable=False, server_default=sa.text("'natural'")),
        sa.Column('expected_farrow', sa.Date()),
        sa.Column('preg_check_date', sa.Date()),
        sa.Column('preg_status', preg_status_enum, nullable=False, server_default=sa.text("'unknown'")),
        sa.Column('parity', sa.Integer()),
        sa.Column('pen_at_service', sa.Text()),
        sa.Column('notes', sa.Text()),
    )

    # Litters
    op.create_table(
        'litters',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sow_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('boar_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('farrow_date', sa.Date()),
        sa.Column('liveborn', sa.Integer(), nullable=True),
        sa.Column('stillborn', sa.Integer(), nullable=True),
        sa.Column('neonatal_deaths', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('wean_date', sa.Date()),
        sa.CheckConstraint('liveborn >= 0', name='ck_litters_liveborn_nonneg'),
        sa.CheckConstraint('stillborn >= 0', name='ck_litters_stillborn_nonneg'),
        sa.CheckConstraint('neonatal_deaths >= 0', name='ck_litters_neodeaths_nonneg'),
    )

    # HealthEvents
    op.create_table(
        'health_events',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id'), nullable=True),
        sa.Column('pen', sa.Text()),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('diagnosis', sa.Text()),
        sa.Column('product', sa.Text()),
        sa.Column('dose', sa.Text()),
        sa.Column('route', sa.Text()),
        sa.Column('vet_name', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('cost', sa.Numeric(10,2)),
        sa.CheckConstraint('cost IS NULL OR cost >= 0', name='ck_health_events_cost_nonneg'),
    )

    # Tasks
    op.create_table(
        'tasks',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('assigned_to', psql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('link_type', link_type_enum),
        sa.Column('link_id', psql.UUID(as_uuid=True)),
        sa.Column('status', task_status_enum, nullable=False, server_default=sa.text("'open'")),
        sa.Column('priority', priority_enum, nullable=False, server_default=sa.text("'med'")),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Files
    op.create_table(
        'files',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pig_id', psql.UUID(as_uuid=True), sa.ForeignKey('pigs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', file_kind_enum, nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    # Drop in reverse order of dependencies
    op.drop_table('files')
    op.drop_table('tasks')
    op.drop_table('health_events')
    op.drop_table('litters')
    op.drop_table('breeding_events')
    op.drop_index('ix_weight_records_pig_date', table_name='weight_records')
    op.drop_table('weight_records')
    op.drop_index('ix_pigs_ear_tag', table_name='pigs')
    op.drop_table('pigs')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    # Enums
    for enum_name in [
        'file_kind', 'task_priority', 'task_status', 'task_link_type',
        'preg_status', 'service_method', 'pig_status', 'pig_class', 'pig_sex', 'user_role'
    ]:
        try:
            sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
        except Exception:
            pass
