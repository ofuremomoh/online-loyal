"""empty message

Revision ID: 19579528138c
Revises: d44814f564a2
Create Date: 2023-01-27 02:28:30.127425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19579528138c'
down_revision = 'd44814f564a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('item_number', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.Column('rendered_data', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('collect',
    sa.Column('collector_id', sa.Integer(), nullable=False),
    sa.Column('collected_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['collected_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['collector_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('collector_id', 'collected_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('collect')
    op.drop_table('product')
    # ### end Alembic commands ###
