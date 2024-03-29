"""empty message

Revision ID: 7d054f8a4243
Revises: bd99a267a62f
Create Date: 2024-03-09 21:20:21.643648

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d054f8a4243"
down_revision: Union[str, None] = "bd99a267a62f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("tg_id", sa.VARCHAR(length=11), nullable=True)
    )
    op.create_unique_constraint(None, "user", ["tg_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user", type_="unique")
    op.drop_column("user", "tg_id")
    # ### end Alembic commands ###
