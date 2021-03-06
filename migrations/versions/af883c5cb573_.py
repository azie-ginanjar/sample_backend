"""empty message

Revision ID: af883c5cb573
Revises: 8a733a25dd3c
Create Date: 2019-06-19 04:37:19.677436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af883c5cb573'
down_revision = '8a733a25dd3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_type', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('email_from_name', sa.String(), nullable=True),
    sa.Column('email_to', sa.String(), nullable=True),
    sa.Column('email_body', sa.String(), nullable=True),
    sa.Column('status_code', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('epoch_created_at', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_v2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('email_log')
    # ### end Alembic commands ###
