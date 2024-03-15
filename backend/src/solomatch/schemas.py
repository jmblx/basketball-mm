from pydantic import BaseModel, UUID4


class PlayerMatchResult(BaseModel):
    id: UUID4
    score: int


class SetSoloMatchResult(BaseModel):
    first_player_result: PlayerMatchResult
    second_player_result: PlayerMatchResult


class Message(BaseModel):
    match_result: str
    solo_rating_change: int
    current_solo_rating: int
    opponent_nickname: str
    telegram_id: int
