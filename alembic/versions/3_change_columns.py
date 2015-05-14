"""
3 change columns

Current ID: e6f87b4a6d
Previous ID: 38ba69ceda4
Timestamp: 2015-05-13 20:26:09.312368
"""
from alembic import op
import sqlalchemy as sa


revision = 'e6f87b4a6d'
down_revision = '38ba69ceda4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('characters', sa.Column('full_name', sa.UnicodeText(), nullable=True))


def downgrade():
    op.drop_column('characters', 'full_name')
