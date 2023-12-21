"""empty message

Revision ID: cc69ff87fcff
Revises: 77766dfa324e
Create Date: 2023-12-20 23:10:35.307333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cc69ff87fcff'
down_revision: Union[str, None] = '77766dfa324e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('match', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('solomatch', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('solomatch', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('match', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###
