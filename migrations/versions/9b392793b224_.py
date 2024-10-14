"""empty message

Revision ID: 9b392793b224
Revises: be2862ea04b8
Create Date: 2024-07-18 09:16:39.384369

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9b392793b224'
down_revision = 'be2862ea04b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payor_email', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('payor_phone', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.drop_column('payor_phone')
        batch_op.drop_column('payor_email')

    # ### end Alembic commands ###