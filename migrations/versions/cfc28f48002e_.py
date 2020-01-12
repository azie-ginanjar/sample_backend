"""empty message

Revision ID: cfc28f48002e
Revises: bee44c417304
Create Date: 2019-06-25 13:46:39.924373

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cfc28f48002e'
down_revision = 'bee44c417304'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist_experience_application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('experience_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('images', postgresql.ARRAY(sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['experience_id'], ['experience.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_v2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('buy_experience',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('experience_id', sa.Integer(), nullable=True),
    sa.Column('number_of_slots', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('epoch_created_at', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['experience_id'], ['experience.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('buy_experience')
    op.drop_table('artist_experience_application')
    # ### end Alembic commands ###