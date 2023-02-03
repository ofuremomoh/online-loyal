"""empty message

Revision ID: d44814f564a2
Revises: 235b3ef93c89
Create Date: 2023-01-26 18:03:28.955310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd44814f564a2'
down_revision = '235b3ef93c89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('loyalty', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'loyalty')
    # ### end Alembic commands ###
