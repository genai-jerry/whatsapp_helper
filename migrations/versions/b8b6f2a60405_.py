"""empty message

Revision ID: b8b6f2a60405
Revises: 32f756e7144b
Create Date: 2024-10-16 20:23:41.128613

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b8b6f2a60405'
down_revision = '32f756e7144b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('win_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('wins', schema=None) as batch_op:
        batch_op.add_column(sa.Column('win_type', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'win_types', ['win_type'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wins', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('win_type')
    op.drop_table('win_types')
    # ### end Alembic commands ###
