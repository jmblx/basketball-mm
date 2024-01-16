from pydantic import BaseModel

from solomatch.schemas import PlayerMatchResult


class TeamResult(BaseModel):
    team_id: int
    result: dict[str, PlayerMatchResult]


class SetMatchResultRequest5x5(BaseModel):
    team1: TeamResult
    team2: TeamResult
