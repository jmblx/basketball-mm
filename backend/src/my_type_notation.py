import datetime
from typing import Annotated

from sqlalchemy import text, JSON, ForeignKey  # , ForeignKey
from sqlalchemy.orm import mapped_column

# Базовые аннотации для моделей БД
added_at = Annotated[
    datetime.datetime,
    mapped_column(
        nullable=True, server_default=text("TIMEZONE('utc', now())")
    ),
]

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

# intfk = Annotated[int, mapped_column(ForeignKey(
#   "match.id", primary_key=True)
# )]
default_int = Annotated[
    int,
    mapped_column(
        nullable=True,
        default=0,
    ),
]

scores_mm = Annotated[dict, mapped_column(JSON, nullable=True)]

winrate = Annotated[float, mapped_column(nullable=True, default=0)]

team_fk = Annotated[int, mapped_column(ForeignKey("team.id"), nullable=True)]
