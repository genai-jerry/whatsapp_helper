"""empty message

Revision ID: bc70b9eb5a6b
Revises: 46cfe049297f
Create Date: 2024-03-28 15:28:14.663920

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bc70b9eb5a6b'
down_revision = '46cfe049297f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
   with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_column('verified')

    # ### end Alembic commands ###