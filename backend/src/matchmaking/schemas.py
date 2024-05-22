from pydantic import BaseModel, UUID4


class PlayerMatchResult(BaseModel):
    id: str
    score: int


class TeamResult(BaseModel):
    team_id: int
    result: dict[str, PlayerMatchResult]


class SetMatchResultRequest5x5(BaseModel):
    team1: TeamResult
    team2: TeamResult


class SetSoloMatchResult(BaseModel):
    first_player_result: PlayerMatchResult
    second_player_result: PlayerMatchResult


class Message(BaseModel):
    match_type: str
    match_result: str
    solo_rating_change: int
    current_solo_rating: int
    opponent_nickname: str
    telegram_id: int
