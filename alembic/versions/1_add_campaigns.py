"""
1 Add campaigns

Current ID: 1fe86c0d74c
Previous ID: 2879aca2220
Timestamp: 2015-05-02 13:43:37.358200
"""
from alembic import op
import sqlalchemy as sa


revision = '1fe86c0d74c'
down_revision = '2879aca2220'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'campaign_memberships',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('is_gm', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'campaign_id')
    )


def downgrade():
    op.drop_table('campaign_memberships')
    op.drop_table('campaigns')
