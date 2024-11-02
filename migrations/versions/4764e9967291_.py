"""empty message

Revision ID: 4764e9967291
Revises: cf202cdc717d
Create Date: 2024-10-30 18:42:47.468011

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4764e9967291'
down_revision = 'cf202cdc717d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('call_setter', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'sales_agent', ['call_setter'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('call_setter')
    # ### end Alembic commands ###
