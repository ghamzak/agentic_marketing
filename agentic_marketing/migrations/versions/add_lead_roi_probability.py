"""
Alembic migration to add predicted_ROI and predicted_probability columns to leads table.
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_lead_roi_probability'
down_revision = '24844dd40606'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('leads', sa.Column('predicted_ROI', sa.Float(), nullable=True))
    op.add_column('leads', sa.Column('predicted_probability', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('leads', 'predicted_ROI')
    op.drop_column('leads', 'predicted_probability')
