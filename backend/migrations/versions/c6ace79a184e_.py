"""empty message

Revision ID: c6ace79a184e
Revises: e0d82cdf4a25
Create Date: 2024-01-10 19:38:06.814911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c6ace79a184e'
down_revision: Union[str, None] = 'e0d82cdf4a25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('match', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished',
                                             'cancelled', name='statusevent'),
               nullable=True)
    op.alter_column('match_5x5', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished',
                                             'cancelled', name='statusevent'),
               nullable=True)
    op.alter_column('solomatch', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished',
                                             'cancelled', name='statusevent'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('solomatch', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished', name='statusevent'),
               nullable=False)
    op.alter_column('match_5x5', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished', name='statusevent'),
               nullable=False)
    op.alter_column('match', 'status',
               existing_type=postgresql.ENUM('opened', 'pending', 'actived', 'finished', name='statusevent'),
               nullable=False)
    # ### end Alembic commands ###
