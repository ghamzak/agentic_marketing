"""
Revision ID: bd377c44ac71
Revises: 878d4a312ad6
Create Date: 2025-07-16 22:18:12.591758

"""

revision = "bd377c44ac71"
down_revision = '878d4a312ad6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('businesses', 'insta_description')
    op.drop_column('businesses', 'insta_url')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('businesses', sa.Column('insta_url', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.add_column('businesses', sa.Column('insta_description', sa.TEXT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
