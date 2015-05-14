"""
4 not null

Current ID: 3a53c48a2a5
Previous ID: e6f87b4a6d
Timestamp: 2015-05-13 20:38:15.931023
"""
from alembic import op
import sqlalchemy as sa

revision = '3a53c48a2a5'
down_revision = 'e6f87b4a6d'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('characters', 'user_id', existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    op.alter_column('characters', 'user_id', existing_type=sa.INTEGER(), nullable=True)
