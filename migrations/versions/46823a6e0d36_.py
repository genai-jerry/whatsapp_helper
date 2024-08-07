"""empty message

Revision ID: 46823a6e0d36
Revises: d7a5725199e1
Create Date: 2024-08-07 18:47:04.466662

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '46823a6e0d36'
down_revision = 'd7a5725199e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('appointment_number', sa.String(length=15), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_column('appointment_number')

    # ### end Alembic commands ###
