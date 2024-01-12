import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
    match = await session.get(Match5x5, match_id)
    match.end_date = datetime.datetime.utcnow()
    await session.merge(match)

    total_score_team1 = sum(player.score for player
                            in match_result.team1.result.values())
    total_score_team2 = sum(player.score for player
                            in match_result.team2.result.values())

    winner_id = match_result.team1.team_id\
        if total_score_team1 > total_score_team2 else total_score_team2
    loser_id = match_result.team1.team_id if winner_id == \
        match_result.team2.team_id else match_result.team2.team_id

    await session.execute(
        update(Match5x5)
        .where(Match5x5.id == match_id)
        .values(winner_id=winner_id)
    )

    winning_team = (await session.execute(
        select(Team).options(joinedload(Team.players)).where(Team.id == winner_id)
    )).unique().scalar_one()

    losing_team = (await session.execute(
        select(Team).options(joinedload(Team.players)).where(Team.id == loser_id)
    )).unique().scalar_one()

    for player in winning_team.players:
        player.match5x5_wins += 1
        player.match5x5_played += 1
        player.match5x5_winrate = player.match5x5_wins / \
            player.match5x5_played * 100
        await session.merge(player)

    for player in losing_team.players:
        player.match5x5_loses += 1
        player.match5x5_played += 1
        player.match5x5_winrate = player.match5x5_wins / \
            player.match5x5_played * 100
        await session.merge(player)

    await session.commit()
    return {"details": f"Success"}
