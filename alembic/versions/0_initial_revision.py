"""
0 initial revision

Current ID: 2879aca2220
Previous ID: None
Timestamp: 2015-04-26 19:43:20.884634
"""
from alembic import op
import sqlalchemy as sa


revision = '2879aca2220'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.UnicodeText(), nullable=False),
        sa.Column('password', sa.UnicodeText(), nullable=False),
        sa.Column('joined', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('users')
