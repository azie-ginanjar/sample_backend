"""empty message

Revision ID: 8a733a25dd3c
Revises: 8e70f2f40ee6
Create Date: 2019-06-19 04:22:13.097149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a733a25dd3c'
down_revision = '8e70f2f40ee6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_email', 'user_v2', ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_email', 'user_v2', type_='unique')
    # ### end Alembic commands ###
