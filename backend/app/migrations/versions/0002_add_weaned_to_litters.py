from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_weaned_to_litters'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('litters', sa.Column('weaned', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('litters', 'weaned')

