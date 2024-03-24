"""empty message

Revision ID: a23c435dc66b
Revises: bc4392bbc2ed
Create Date: 2024-01-23 13:07:03.596511

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a23c435dc66b"
down_revision: Union[str, None] = "bc4392bbc2ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "team", ["name"])
    op.create_unique_constraint(None, "user", ["nickname"])
    op.drop_column("user", "searching")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column(
            "searching", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(None, "user", type_="unique")
    op.drop_constraint(None, "team", type_="unique")
    # ### end Alembic commands ###
