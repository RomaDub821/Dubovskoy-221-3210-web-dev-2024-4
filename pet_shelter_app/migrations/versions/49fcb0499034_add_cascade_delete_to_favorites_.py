"""Add cascade delete to favorites relationship

Revision ID: 49fcb0499034
Revises: f67d1a090d79
Create Date: 2024-06-06 03:38:47.703958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49fcb0499034'
down_revision = 'f67d1a090d79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.drop_constraint('favorites_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('favorites_ibfk_2', 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###