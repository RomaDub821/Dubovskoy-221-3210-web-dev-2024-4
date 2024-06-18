"""full

Revision ID: 4c1ab61216b5
Revises: 21852c66290b
Create Date: 2024-06-18 00:14:00.096712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c1ab61216b5'
down_revision = '21852c66290b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book_genre', schema=None) as batch_op:
        batch_op.drop_constraint('book_genre_ibfk_1', type_='foreignkey')
        batch_op.drop_constraint('book_genre_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'genre', ['genre_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'book', ['book_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book_genre', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('book_genre_ibfk_2', 'genre', ['genre_id'], ['id'])
        batch_op.create_foreign_key('book_genre_ibfk_1', 'book', ['book_id'], ['id'])

    # ### end Alembic commands ###