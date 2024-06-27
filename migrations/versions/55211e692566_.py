"""empty message

Revision ID: 55211e692566
Revises: 790e1db3146c
Create Date: 2024-06-27 13:33:04.986799

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '55211e692566'
down_revision = '790e1db3146c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_mode',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sale',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sale_value', sa.Integer(), nullable=False),
    sa.Column('total_paid', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=255), nullable=True),
    sa.Column('note', sa.String(length=255), nullable=True),
    sa.Column('sale_date', sa.DateTime(), nullable=True),
    sa.Column('is_final', sa.Boolean(), nullable=False),
    sa.Column('opportunity_id', sa.Integer(), nullable=True),
    sa.Column('sales_agent', sa.Integer(), nullable=True),
    sa.Column('product', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunity.id'], ),
    sa.ForeignKeyConstraint(['product'], ['products.id'], ),
    sa.ForeignKeyConstraint(['sales_agent'], ['sales_agent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_value', sa.Integer(), nullable=False),
    sa.Column('charges', sa.Integer(), nullable=False),
    sa.Column('payment_mode_reference', sa.String(length=255), nullable=True),
    sa.Column('currency', sa.String(length=255), nullable=True),
    sa.Column('payment_date', sa.DateTime(), nullable=False),
    sa.Column('is_deposit', sa.Boolean(), nullable=False),
    sa.Column('invoice_link', sa.String(length=255), nullable=True),
    sa.Column('sale', sa.Integer(), nullable=True),
    sa.Column('opportunity', sa.Integer(), nullable=True),
    sa.Column('accountant', sa.Integer(), nullable=True),
    sa.Column('payment_mode', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['accountant'], ['users.id'], ),
    sa.ForeignKeyConstraint(['opportunity'], ['opportunity.id'], ),
    sa.ForeignKeyConstraint(['payment_mode'], ['payment_mode.id'], ),
    sa.ForeignKeyConstraint(['sale'], ['sale.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.drop_column('sales_date')

    with op.batch_alter_table('user_role', schema=None) as batch_op:
        batch_op.alter_column('role_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_role', schema=None) as batch_op:
        batch_op.alter_column('role_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sales_date', mysql.DATETIME(), nullable=True))

    op.drop_table('payments')
    op.drop_table('sale')
    op.drop_table('products')
    op.drop_table('payment_mode')
    # ### end Alembic commands ###
