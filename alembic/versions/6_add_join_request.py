"""
6 add join request

Current ID: 31a1004438a
Previous ID: 4373dfdaa05
Timestamp: 2015-06-28 14:58:58.296747
"""
from alembic import op
import sqlalchemy as sa

revision = '31a1004438a'
down_revision = '4373dfdaa05'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('campaigns', sa.Column('description', sa.UnicodeText(), nullable=True))
    op.add_column('memberships', sa.Column('status', sa.Integer(), nullable=False))
    op.drop_column('memberships', 'is_gm')


def downgrade():
    op.add_column('memberships', sa.Column('is_gm', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('memberships', 'status')
    op.drop_column('campaigns', 'description')
