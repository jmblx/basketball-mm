from typing import List
import uuid

from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from my_type_notation import added_at, intpk


# модель пользователя для базы данных
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    nickname: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    roles: Mapped[list["Role"]] = relationship(
        back_populates="user", uselist=True
    )
    email: Mapped[str] = mapped_column()
    is_email_confirmed: Mapped[bool] = mapped_column(default=False)
    email_confirmation_token = mapped_column(nullable=True, type_=String(50))
    registered_at: Mapped[added_at]
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=True)
    teams: Mapped[list["Team"]] = relationship(
        back_populates="players", secondary="user_team", uselist=True
    )
    pathfile: Mapped[str] = mapped_column(nullable=True)
    searching: Mapped[bool] = mapped_column(default=False)
    solo_raiting: Mapped[int] = mapped_column(default=2500)
    solomatches = relationship(
        "SoloMatch",
        back_populates="players",
        uselist=True,
        secondary="user_solomatch"
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    permissions: Mapped[JSON] = mapped_column(JSON)
    user: Mapped["User"] = relationship(back_populates="roles", uselist=False)


class Team(Base):
    __tablename__ = "team"

    id: Mapped[intpk]
    name: Mapped[str]
    number: Mapped[int] = mapped_column(nullable=True)
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
    pathfile: Mapped[str]


class UserTeam(Base):
    __tablename__ = "user_team"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id"), primary_key=True
    )
