import datetime
import enum
import math
from typing import List, Annotated

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth.models import Team, User
from database import Base
from my_type_notation import intpk, added_at, scores_mm, team_fk


class StatusEvent(enum.Enum):
    opened = "OPENED"
    pending = "PENDING"
    actived = "ACTIVED"
    finished = "FINISHED"
    cancelled = "CANCELLED"


class Tournament(Base):
    __tablename__ = "tournament"

    @staticmethod
    def default_number_stages(context):
        return int(
            math.log2(context.get_current_parameters()["number_participants"])
        )

    id: Mapped[intpk]
    status: Mapped[StatusEvent]
    placemark: Mapped[str]
    number_participants: Mapped[int]
    number_stages: Mapped[int] = mapped_column(default=default_number_stages)
    winner_id: Mapped[int] = mapped_column(
        ForeignKey("team.id"), nullable=True
    )
    start_date: Mapped[added_at] = mapped_column(nullable=True)
    end_date: Mapped[added_at]
    teams: Mapped[List["Team"]] = relationship(
        back_populates="tournament",
        uselist=True,
        secondary="team_tournament",
    )
    matches: Mapped[List["Match"]] = relationship(
        back_populates="tournament",
        uselist=True,
    )
    pathfile: Mapped[str]


class ParentMatch:
    id: Mapped[intpk]
    status: Mapped[StatusEvent] = mapped_column(nullable=True)
    start_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    end_date: Mapped[datetime.datetime] = mapped_column(nullable=True)


class NotSoloMatch:
    winner_id: Mapped[team_fk]
    loser_id: Mapped[team_fk]


class Match(Base, ParentMatch, NotSoloMatch):
    __tablename__ = "match"

    teams: Mapped[List["Team"]] = relationship(
        back_populates="matches", uselist=True, secondary="team_match"
    )
    stage: Mapped[int] = mapped_column(nullable=True)
    number_in_stage: Mapped[int] = mapped_column(nullable=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    tournament: Mapped["Tournament"] = relationship(
        back_populates="matches", uselist=False
    )


class Match5x5(Base, ParentMatch, NotSoloMatch):
    __tablename__ = "match_5x5"

    scores: Mapped[scores_mm]
    teams: Mapped[List["Team"]] = relationship(
        "Team",
        back_populates="matches_5x5",
        uselist=True,
        secondary="team_match_5x5",
    )


class SoloMatch(Base, ParentMatch):
    __tablename__ = "solomatch"

    players: Mapped[List["User"]] = relationship(
        "User",
        back_populates="solomatches",
        uselist=True,
        secondary="user_solomatch",
    )
    scores: Mapped[scores_mm]
    winner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    loser_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)


class TeamMatchBase:

    id: Mapped[intpk]
    team_fk: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=True)


class TeamMatch(Base, TeamMatchBase):
    __tablename__ = "team_match"

    match_fk: Mapped[int] = mapped_column(ForeignKey("match.id"))


class TeamMatch5x5(Base, TeamMatchBase):
    __tablename__ = "team_match_5x5"

    match_fk: Mapped[int] = mapped_column(ForeignKey("match_5x5.id"))


class UserSoloMatch(Base):
    __tablename__ = "user_solomatch"

    id: Mapped[intpk]
    user_fk: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    solomatch_fk: Mapped[int] = mapped_column(ForeignKey("solomatch.id"))


class TeamTournament(Base):
    __tablename__ = "team_tournament"

    id: Mapped[intpk]
    team_fk: Mapped[int] = mapped_column(ForeignKey("team.id"))
    tournament_fk: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
