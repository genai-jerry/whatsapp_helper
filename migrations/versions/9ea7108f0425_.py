"""empty message

Revision ID: 9ea7108f0425
Revises: 8636e18f5aac
Create Date: 2024-06-07 16:06:23.050299

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9ea7108f0425'
down_revision = '8636e18f5aac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('challenge_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('instances', schema=None) as batch_op:
        batch_op.alter_column('sms_idea_api_key',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=False)

    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('company_type', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('challenge_type', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'company_type', ['company_type'], ['id'])
        batch_op.create_foreign_key(None, 'challenge_type', ['challenge_type'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('campaign', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_general_ci', length=250), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('challenge_type')
        batch_op.drop_column('company_type')
        batch_op.drop_column('gender')

    with op.batch_alter_table('instances', schema=None) as batch_op:
        batch_op.alter_column('sms_idea_api_key',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=True)

    op.drop_table('company_type')
    op.drop_table('challenge_type')
    # ### end Alembic commands ###
