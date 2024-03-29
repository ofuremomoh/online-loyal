"""empty message

Revision ID: 095e4e9fdb4b
Revises: 869fe712d6ab
Create Date: 2023-01-26 17:11:11.148619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '095e4e9fdb4b'
down_revision = '869fe712d6ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_type', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['merchant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    # ### end Alembic commands ###
