"""
5 rename memberships

Current ID: 4373dfdaa05
Previous ID: 3a53c48a2a5
Timestamp: 2015-05-14 01:14:42.271262
"""
from alembic import op


revision = '4373dfdaa05'
down_revision = '3a53c48a2a5'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('campaign_memberships', 'memberships')


def downgrade():
    op.rename_table('memberships', 'campaign_memberships')
