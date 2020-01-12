"""empty message

Revision ID: d729c682332e
Revises: af1cbd9469b1
Create Date: 2019-06-20 19:53:26.902467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd729c682332e'
down_revision = 'af1cbd9469b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('experience',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('policy', sa.String(), nullable=True),
    sa.Column('guest_price', sa.Float(), nullable=True),
    sa.Column('artist_booking_price', sa.Float(), nullable=True),
    sa.Column('guest_slot', sa.Integer(), nullable=True),
    sa.Column('artist_slot', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.String(), nullable=True),
    sa.Column('epoch_start_date', sa.Integer(), nullable=True),
    sa.Column('end_date', sa.String(), nullable=True),
    sa.Column('epoch_end_date', sa.Integer(), nullable=True),
    sa.Column('pincode', sa.String(), nullable=True),
    sa.Column('can_apply', sa.Boolean(), nullable=True),
    sa.Column('can_purchase', sa.Boolean(), nullable=True),
    sa.Column('potential_to_earn', sa.Float(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('epoch_created_at', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('experience')
    # ### end Alembic commands ###