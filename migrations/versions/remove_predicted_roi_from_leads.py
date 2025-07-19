"""
Alembic migration to remove the predicted_ROI column from the leads table.
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table('leads') as batch_op:
        batch_op.drop_column('predicted_ROI')

def downgrade():
    with op.batch_alter_table('leads') as batch_op:
        batch_op.add_column(sa.Column('predicted_ROI', sa.Float))
