"""
Initial revision

Current ID: 1fac369d356
Previous ID: None
Timestamp: 2015-04-26 15:11:44.446117
"""
from alembic import op
import sqlalchemy as sa


revision = '1fac369d356'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('email', sa.Unicode(length=255), nullable=False),
        sa.Column('password', sa.Unicode(length=255), nullable=False),
        sa.Column('joined', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('users')
