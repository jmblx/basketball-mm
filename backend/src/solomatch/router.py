import fastapi
from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session
from solomatch.schemas import SetMatchResultRequest
from tournaments.models import SoloMatch

router = fastapi.APIRouter(prefix="/solomatch", tags=["matchmaking"])


@router.put("/set-match-result")
async def set_solomatch_result(
    match_id: int,
    match_result: SetMatchResultRequest,
    session: AsyncSession = Depends(get_async_session),
):
    first_player_id = match_result.first_player_result.id
    first_player_score = match_result.first_player_result.score
    second_player_id = match_result.second_player_result.id
    second_player_score = match_result.second_player_result.score

    winner_id = first_player_id if first_player_score\
        > second_player_score else second_player_id
    loser_id = first_player_id if first_player_score\
        < second_player_score else second_player_id

    # Обновление результата матча
    await session.execute(
        update(SoloMatch)
        .where(SoloMatch.id == match_id)
        .values({
            "winner_id": winner_id,
            "scores": {
                "first_player": {
                    "id": str(first_player_id),
                    "score": first_player_score
                },
                "second_player": {
                    "id": str(second_player_id),
                    "score": second_player_score
                }
            }
        })
    )

    winner_stats = await session.get(User, winner_id)
    loser_stats = await session.get(User, loser_id)

    winner_wins = winner_stats.solomatch_wins + 1
    winner_winrate = winner_wins / (winner_wins + winner_stats.solomatch_loses) * 100
    await session.execute(
        update(User)
        .where(User.id == winner_id)
        .values(solomatch_wins=winner_wins, solomatch_winrate=winner_winrate)
    )

    loser_loses = loser_stats.solomatch_loses + 1
    loser_winrate = loser_stats.solomatch_wins / (loser_stats.solomatch_wins + loser_loses) * 100
    await session.execute(
        update(User)
        .where(User.id == loser_id)
        .values(solomatch_loses=loser_loses, solomatch_winrate=loser_winrate)
    )

    await session.commit()
    return {"details": f"now in match with id = {match_id} winner is {winner_id}"}

