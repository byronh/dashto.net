"""
2 Add characters

Current ID: 38ba69ceda4
Previous ID: 1fe86c0d74c
Timestamp: 2015-05-03 16:35:06.336757
"""
from alembic import op
import sqlalchemy as sa


revision = '38ba69ceda4'
down_revision = '1fe86c0d74c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'characters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('portrait', sa.Unicode(length=2048), nullable=True),
        sa.Column('biography', sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('characters')
