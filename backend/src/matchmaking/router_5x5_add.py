from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import Team
from database import get_async_session
from matchmaking.schemas import SetMatchResultRequest5x5
from tournaments.models import Match5x5

router = APIRouter(prefix="", tags=["matchmaking"])

@router.put("/set-match5x5-result")
async def set_match5x5_result(
    match_id: int,
    match_result: SetMatchResultRequest5x5,
    session: AsyncSession = Depends(get_async_session),
):
    winning_team_id = match_result.winning_team_id
    losing_team_id = match_result.losing_team_id

    # Обновление результата матча
    await session.execute(
        update(Match5x5)
        .where(Match5x5.id == match_id)
        .values(winner_team_id=winning_team_id)
    )

    winning_team = await session.get(Team, winning_team_id)
    losing_team = await session.get(Team, losing_team_id)

    # Обновление статистики для игроков победившей команды
    for player in winning_team.players:
        player.match5x5_wins += 1
        player.match5x5_played += 1
        player.match5x5_winrate = player.match5x5_wins / player.match5x5_played * 100
        await session.merge(player)

    # Обновление статистики для игроков проигравшей команды
    for player in losing_team.players:
        player.match5x5_loses += 1
        player.match5x5_played += 1
        player.match5x5_winrate = player.match5x5_wins / player.match5x5_played * 100
        await session.merge(player)

    await session.commit()
    return {"details": f"In match {match_id}, the winning team is {winning_team_id}"}
