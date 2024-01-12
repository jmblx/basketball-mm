import os
import shutil

import fastapi
from PIL import Image
from fastapi import Depends, Response, UploadFile
from sqlalchemy import insert, select, func, and_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from auth.base_config import current_user
from auth.models import User, Role, UserTeam, Team
from auth.schemas import RoleSchema, TeamSchema
from database import get_async_session
from constants import images_dir
from tournaments.models import TeamTournament, Tournament, StatusEvent
from utils import create_upload_avatar


router = fastapi.APIRouter(prefix="/team", tags=["teams"])


@router.post("/uploadfile/team/avatar")
async def upload_team_avatar(
    file: UploadFile,
    team_id: int,
):
    class_ = Team
    team_avatar_dir = f"{images_dir}\\team"
    res = await create_upload_avatar(team_id, file, class_, team_avatar_dir)
    return res


@router.post("/join-team")
async def join_team(
    team_id: int,
    response: Response,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = insert(UserTeam).values(
            {
                "user_id": user.id,
                "team_id": team_id,
            }
        )
        await session.execute(stmt)
        await session.commit()
        response.status_code = HTTP_200_OK

    except IntegrityError:
        response.status_code = HTTP_400_BAD_REQUEST
        return {
            "details": f"Invalid data"
            f"(maybe user already registered in team with team_id = {team_id})"
        }


@router.post("/add-new-team")
async def add_new_team(
    team: TeamSchema,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    team = Team(**team.model_dump())
    team.captain_id = user.id
    session.add(team)
    await session.flush()
    stmt = insert(UserTeam).values(
        {"team_id": team.id, "user_id": user.id}
    )
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}


@router.post("/register-team-in-tournament")
async def register_team_in_tournament(
    team_id: int,
    tournament_id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    count_registered = await session.scalar(
        select(func.count())
        .select_from(TeamTournament)
        .where(TeamTournament.tournament_fk == tournament_id)
    )

    query_get_tournament = (
        select(Tournament).where(Tournament.id == tournament_id)
    )
    result_tournament = await session.execute(query_get_tournament)
    tournament: Tournament = result_tournament.scalar()

    query_check_registration = (
        select(func.count())
        .select_from(TeamTournament)
        .where(and_(TeamTournament.team_fk == team_id, TeamTournament.tournament_fk == tournament_id))
    )
    result_check_registration = await session.scalar(query_check_registration)

    if tournament.status == StatusEvent.opened:
        if tournament.number_participants == count_registered+1:
            tournament.status = StatusEvent.pending
        if result_check_registration == 0:
            stmt = insert(TeamTournament).values(
                {"team_fk": team_id, "tournament_fk": tournament_id}
            )
            await session.execute(stmt)
            await session.commit()
            return {"status": "success"}
        else:
            response.status_code = HTTP_400_BAD_REQUEST
            return {"status": "denied", "details": "team is already registered in the tournament"}
    else:
        response.status_code = HTTP_400_BAD_REQUEST
        return {"status": "denied", "details": "tournament not OPENED now"}


@router.post('/change-search-mode')
async def change_search_mode(
    team_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    team = await session.get(Team, team_id)
    if team.captain_id == user.id:
        team.is_captain_only_search = False if team.is_captain_only_search \
            else True
        await session.commit()
        return "Настройки поиска обновлены"
    else:
        return "Ошибка: только капитан может изменить эти настройки"

