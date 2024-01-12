from pydantic import BaseModel, UUID4

class PlayerMatchResult(BaseModel):
    id: UUID4
    score: int

class SetMatchResultRequest(BaseModel):
    first_player_result: PlayerMatchResult
    second_player_result: PlayerMatchResult
