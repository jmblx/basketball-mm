import os
import random
import shutil
from typing import List
from uuid import UUID

import fastapi
from PIL import Image
from fastapi import Depends, Request, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import insert, select, func, and_, update, exc
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from auth.base_config import current_user
from auth.models import User, UserTeam, Team
from auth.schemas import TeamSchema
from database import get_async_session
from constants import IMAGES_DIR
from slugify import slugify

from matchmaking.router import templates
from teams.schemas import TeamUpdate, GetTeamImages
from tournaments.models import TeamTournament, Tournament, StatusEvent
from utils import create_upload_avatar, get_user_attrs, get_object_images

router = fastapi.APIRouter(prefix="/team", tags=["teams"])


@router.post("/uploadfile/team/avatar")
async def upload_team_avatar(
    file: UploadFile,
    team_id: int,
):
    class_ = Team
    team_avatar_dir = os.path.join(IMAGES_DIR, "team")

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
        team = await session.get(Team, team_id)
        team.number += 1
        await session.merge(team)
        await session.commit()
        response.status_code = HTTP_200_OK

    except IntegrityError:
        response.status_code = HTTP_400_BAD_REQUEST
        return {
            "details": f"Invalid data"
            f"(maybe user already registered in team with team_id = {team_id})"
        }
    return {"team_id": team.id}


@router.put("/leave-team")
async def left_team(
    team_id: int,
    response: Response,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.players))
    team = (await session.execute(query)).scalar()
    if team.captain_id == user.id:
        response.status_code = HTTP_400_BAD_REQUEST
        return {"details": "user can't leave until user is captain"}
    if user in team.players:
        team.players.remove(user)
        team.number -= 1
        await session.commit()
        return {"details": "User has successfully left the team"}
    else:
        response.status_code = HTTP_404_NOT_FOUND
        return {"details": "User is not a member of the team"}


@router.post("/add-new-team")
async def add_new_team(
    team_params: TeamSchema,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Создание слага

    team = Team(**team_params.model_dump())
    slug = slugify(team.name, lowercase=True)
    team.slug = slug
    team.captain_id = user.id
    team.players = [user]
    session.add(team)
    await session.commit()
    return {"status": "success", "team_id": team.id}


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


@router.get("/data/{team_slug}")
async def team_data(
    response: Response,
    team_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        team: Team = (await session.execute(
            select(Team)
            .options(joinedload(Team.players), joinedload(Team.captain))
            .where(Team.slug == team_slug)
        )).unique().scalar_one()
    except NoResultFound:
        response.status_code = HTTP_404_NOT_FOUND
        return {"result": "page not found"}
    return {
        "is_captain_only_search": team.is_captain_only_search,
        "team_id": team.id,
        "team_name": team.name,
        "team_captain_nickname": team.captain.nickname,
        "team_captain_id": team.captain.id,
        "number": team.number,  # Количество участников
        "participants": [await get_user_attrs(user) for user in team.players]
    }


@router.get("/image/{team_id}")
async def get_image(
    team_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    team = await session.get(Team, team_id)
    return FileResponse(team.pathfile)


@router.get("/page/{team_slug}")
async def render_team_page(
    request: Request,
):
    return templates.TemplateResponse("team_page.html", {
        "request": request
    })


@router.put("/update/{team_id}")
async def team_update(
    team_id: int,
    team_update: TeamUpdate,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    print(team_update.model_dump())
    if not team_update.name and team_update.is_captain_only_search is None:
        response.status_code = HTTP_404_NOT_FOUND
        return {"status": "error with request. Data is null."}
    update_data = {key: value for key, value in team_update.model_dump().items() if value is not None}
    if "name" in update_data.keys():
        update_data["slug"] = slugify(update_data.get("name"), lowercase=True)
    try:
        await session.execute(update(Team).where(Team.id == team_id).values(update_data))
        await session.commit()
    except exc.IntegrityError:
        await session.rollback()
        update_data["slug"] = f'{update_data["slug"]}-{random.randint(team_id+1, (team_id*10+1747))}'
        await session.execute(update(Team).where(Team.id == team_id).values(update_data))
        await session.commit()
    return {"status": "success"}


@router.get("/check-captainship")
async def check_captainship(
    user_id: UUID,
    team_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    team = await session.get(Team, team_id)
    return {"isCaptain": team.captain_id == user_id}



@router.get("/teams_images/{team_ids}")
async def get_teams_images(
    team_ids: str,
):
    images = await get_object_images(Team, team_ids)
    print(images)

