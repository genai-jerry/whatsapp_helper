"""empty message

Revision ID: 8636e18f5aac
Revises: 7c0679605306
Create Date: 2024-06-06 18:16:08.975574

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8636e18f5aac'
down_revision = '7c0679605306'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instances', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sms_idea_api_key', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instances', schema=None) as batch_op:
        batch_op.drop_column('sms_idea_api_key')
    # ### end Alembic commands ###
