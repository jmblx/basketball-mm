"""empty message

Revision ID: 4225b580c34d
Revises: 33dfa957dfec
Create Date: 2024-01-11 23:56:28.398621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4225b580c34d'
down_revision: Union[str, None] = '33dfa957dfec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass