from pydantic import BaseModel

from solomatch.schemas import PlayerMatchResult


class Team5x5MatchResult(BaseModel):
    player1_match_result: PlayerMatchResult
    player2_match_result: PlayerMatchResult
    player3_match_result: PlayerMatchResult
    player4_match_result: PlayerMatchResult
    player5_match_result: PlayerMatchResult


class SetMatchResultRequest5x5(BaseModel):
    team1_result: Team5x5MatchResult
    team2_result: Team5x5MatchResult

