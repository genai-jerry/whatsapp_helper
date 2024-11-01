"""empty message

Revision ID: 1e0ad635858d
Revises: 615694230186
Create Date: 2024-10-22 15:03:58.304012

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1e0ad635858d'
down_revision = '615694230186'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_projection_config', schema=None) as batch_op:
        batch_op.add_column(sa.Column('marketing_spend_updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_projection_config', schema=None) as batch_op:
        batch_op.drop_column('marketing_spend_updated_at')
    # ### end Alembic commands ###