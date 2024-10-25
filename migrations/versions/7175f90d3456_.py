"""empty message

Revision ID: 7175f90d3456
Revises: 76e43a2d5fd0
Create Date: 2024-10-24 08:16:31.178491

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7175f90d3456'
down_revision = '76e43a2d5fd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_projections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('commission_percentage', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_projections', schema=None) as batch_op:
        batch_op.drop_column('commission_percentage')
   # ### end Alembic commands ###
