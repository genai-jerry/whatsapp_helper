"""empty message

Revision ID: 4c41c746ac39
Revises: 1fb14dfd975d
Create Date: 2024-06-12 10:58:32.409719

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4c41c746ac39'
down_revision = '1fb14dfd975d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lead_event_fired', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('submit_application_event_fired', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('sale_event_fired', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.drop_column('sale_event_fired')
        batch_op.drop_column('submit_application_event_fired')
        batch_op.drop_column('lead_event_fired')

    # ### end Alembic commands ###
