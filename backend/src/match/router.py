import fastapi
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import Team
from database import get_async_session
from tournaments.models import Match5x5
from utils import get_team_card_info, get_user_card_info

router = fastapi.APIRouter(prefix="/match", tags=["matches"])

@router.get("/data")
async def get_match_data(
    match_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    match = (await session.execute(
        select(Match5x5).options(selectinload(Match5x5.teams)
             .selectinload(Team.players)).where(Match5x5.id == match_id)
    )).unique().scalar_one()
    match_info = {
        "match_id": match.id,
        "teams": []
    }

    for team in match.teams:
        team_info = await get_team_card_info(team.id)
        team_players_info = []
        for player in team.players:
            player_info = await get_user_card_info(player.id)
            team_players_info.append(player_info)
        team_info["players"] = team_players_info
        match_info["teams"].append(team_info)

    return match_info

