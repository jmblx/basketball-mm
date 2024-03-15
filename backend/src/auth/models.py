import enum
from typing import List
import uuid

from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyBaseOAuthAccountTableUUID,
)
from sqlalchemy import String, JSON, ForeignKey, DDL, event, VARCHAR, INTEGER
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from my_type_notation import added_at, intpk, default_int, winrate


class League(enum.Enum):
    rookie_rally = "Rookie Rally"
    dribble_drive = "Dribble Drive"
    backboard_bounce = "Backboard Bounce"
    jumpshot_junction = "Jumpshot Junction"
    slam_dunk_summit = "Slam Dunk Summit"
    alley_oop_apex = "Alley-Oop Apex"


class Matchmaking:
    rating_5x5: Mapped[int] = mapped_column(default=1000, nullable=True)
    match5x5_wins: Mapped[default_int]
    match5x5_loses: Mapped[default_int]
    match5x5_winrate: Mapped[winrate]
    match5x5_played: Mapped[default_int]
    # league: Mapped[League]


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


# модель пользователя для базы данных
class User(SQLAlchemyBaseUserTableUUID, Matchmaking, Base):
    __tablename__ = "user"

    @staticmethod
    def default_nickname(context):
        return str(context.get_current_parameters()["email"].split("@")[0])

    nickname: Mapped[str] = mapped_column(default=default_nickname, unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), default=1)
    roles: Mapped[list["Role"]] = relationship(
        back_populates="user", uselist=True
    )
    email: Mapped[str]
    is_email_confirmed: Mapped[bool] = mapped_column(default=False)
    email_confirmation_token = mapped_column(nullable=True, type_=String(50))
    registered_at: Mapped[added_at]
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    phone_number: Mapped[str] = mapped_column(VARCHAR(12), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=True)
    tg_id: Mapped[int] = mapped_column(INTEGER(), nullable=True, unique=True)
    teams: Mapped[list["Team"]] = relationship(
        back_populates="players", secondary="user_team", uselist=True
    )
    captain_teams: Mapped[list["Team"]] = relationship(
        back_populates="captain", uselist=True
    )
    pathfile: Mapped[str] = mapped_column(nullable=True)
    solo_rating: Mapped[int] = mapped_column(default=2501)
    solomatches = relationship(
        "SoloMatch",
        back_populates="players",
        uselist=True,
        secondary="user_solomatch"
    )
    solomatch_wins: Mapped[default_int]
    solomatch_loses: Mapped[default_int]
    solomatch_winrate: Mapped[winrate]
    solomatch_played: Mapped[default_int]
    search_vector = mapped_column(TSVECTOR)
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )


create_index = DDL('CREATE INDEX search_vector_index ON "user" USING GIN(search_vector);')
event.listen(User.__table__, 'after_create', create_index)


class Role(Base):
    __tablename__ = "role"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    permissions: Mapped[dict] = mapped_column(JSON)
    user: Mapped["User"] = relationship(back_populates="roles", uselist=False)


class Team(Matchmaking, Base):
    __tablename__ = "team"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(unique=True, type_=VARCHAR(30))
    slug: Mapped[str] = mapped_column(unique=True, type_=VARCHAR(40))
    number: Mapped[int] = mapped_column(default=1)
    captain_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    captain: Mapped["User"] = relationship(
        back_populates="captain_teams", uselist=False
    )
    is_captain_only_search: Mapped[bool] = mapped_column(default=False)
    players: Mapped[list["User"]] = relationship(
        back_populates="teams", secondary="user_team", uselist=True
    )
    tournament = relationship(
        "Tournament",
        back_populates="teams",
        uselist=True,
        secondary="team_tournament",
    )
    matches = relationship(
        "Match",
        back_populates="teams",
        uselist=True,
        secondary="team_match"
    )
    matches_5x5 = relationship(
        "Match5x5",
        back_populates="teams",
        uselist=True,
        secondary="team_match_5x5"
    )
    pathfile: Mapped[str]


class UserTeam(Base):
    __tablename__ = "user_team"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id"), primary_key=True
    )
