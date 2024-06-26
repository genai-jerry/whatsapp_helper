"""empty message

Revision ID: b0ca74d779a2
Revises: 790e1db3146c
Create Date: 2024-06-30 22:00:31.007862

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b0ca74d779a2'
down_revision = '790e1db3146c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ad_placement', sa.String(length=250), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.drop_column('ad_placement')

    # ### end Alembic commands ###
