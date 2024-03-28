"""empty message

Revision ID: 46cfe049297f
Revises: 63da8105168b
Create Date: 2024-03-28 14:22:05.611820

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '46cfe049297f'
down_revision = '63da8105168b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('max_scores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('max_scores', schema=None) as batch_op:
        batch_op.drop_column('category')

    # ### end Alembic commands ###
