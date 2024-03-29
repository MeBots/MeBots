"""add timestamps

Revision ID: 002602fd57cb
Revises: 29a41197e9a8
Create Date: 2022-10-16 21:04:58.118759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002602fd57cb'
down_revision = '29a41197e9a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bot', sa.Column('created', sa.Integer(), nullable=True))
    op.add_column('bot', sa.Column('updated', sa.Integer(), nullable=True))
    op.add_column('instance', sa.Column('created', sa.Integer(), nullable=True))
    op.add_column('instance', sa.Column('updated', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('registered', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'registered')
    op.drop_column('instance', 'updated')
    op.drop_column('instance', 'created')
    op.drop_column('bot', 'updated')
    op.drop_column('bot', 'created')
    # ### end Alembic commands ###
