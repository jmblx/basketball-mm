import fastapi
from PIL import Image
from fastapi import Depends, Response, UploadFile
from fastapi_cache.decorator import cache
from sqlalchemy import insert, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from constants import images_dir
from database import get_async_session
from tournaments.models import Tournament, Match, TeamMatch, StatusEvent
from tournaments.schemas import TournamentSchema
from tournaments.utils import fill_tournament, get_data, fill_tournament_teams, get_tournaments
from auth.models import User
from utils import create_upload_avatar

router = fastapi.APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.put("/upload/avatar")
async def upload_tournament_avatar(
    file: UploadFile,
    tournament_id: int,
):
    class_ = Tournament
    tournament_avatar_dir = f"{images_dir}\\tournament"
    res = await create_upload_avatar(tournament_id, file, class_, tournament_avatar_dir)
    return res


@router.get("/get/tournaments/opened")
@cache(expire=60)
async def get_opened_tournaments():
    result = await get_tournaments(StatusEvent.opened)
    return result


@router.put("/update/tournament")
async def update_tournament(
    tournament_id: int,
    tournament: TournamentSchema,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(Tournament)
        .where(Tournament.id == tournament_id)
        .values(**tournament.model_dump())
    )
    await session.execute(stmt)
    return {"status": "success", "data": tournament.__dict__, "details": None}


@router.post("/add/tournament")
async def add_new_tournament(
    new_tournament: TournamentSchema,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    new_tournament_instance = Tournament(**new_tournament.model_dump())
    session.add(new_tournament_instance)
    await session.flush()
    tournament_id = new_tournament_instance.id
    await fill_tournament(tournament_id, session)
    await session.commit()
    response.status_code = HTTP_201_CREATED
    return {"status": "success"}


@router.post("/start-tournament")
async def start_tournament(
    tournament_id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    tournament_status = await get_data(
        class_=Tournament.status,
        is_scalar=True,
        filter=Tournament.id == tournament_id
    )
    if tournament_status == StatusEvent.pending:
        await fill_tournament_teams(tournament_id)
        response.status_code = HTTP_200_OK
        return {"status": "success"}
    else:
        response.status_code = HTTP_400_BAD_REQUEST
        return {"details": "tournament not pending"}


@router.post("/set/match-tournament/result")
async def set_match_result(
    match_id: int,
    winner_id: int,
    tournament_id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    test = await session.get(Match, match_id)
    if test.winner_id:
        print(test)
        response.status_code = HTTP_400_BAD_REQUEST
        return {"details": "match already ended"}
    stmt_update_res = (
        update(Match)
        .where(Match.id == match_id)
        .values({"winner_id": winner_id})
    )
    await session.execute(stmt_update_res)
    match: Match = await get_data(Match, Match.id == match_id, is_scalar=True)
    tournament = await session.get(Tournament, tournament_id, options=selectinload(Tournament.matches))

    next_stage = match.stage + 1
    new_number_in_stage = match.number_in_stage // 2
    new_match_id = await get_data(
        Match.id,
        and_(
                Match.number_in_stage == new_number_in_stage,
                Match.stage == next_stage,
                Match.tournament_id == tournament.id
            ),
        is_scalar=True,
    )

    sub_stmt = (
        select(TeamMatch.id)
        .where(and_(
            TeamMatch.match_fk == new_match_id,
            TeamMatch.team_fk == None
        )
        )
        .limit(1)
    )
    res = (await session.execute(sub_stmt)).scalar()
    if res == None:
        tournament.winner_id = winner_id
        tournament.status = StatusEvent.finished

    stmt_set_member_match = (
        update(TeamMatch)
        .where(TeamMatch.id == sub_stmt)
        .values({"team_fk": winner_id})
    )
    await session.execute(stmt_set_member_match)
    # await session.flush()
    # stmt_debug = (
    #     select(TeamMatch.team_fk)
    #     .where(TeamMatch.match_fk == new_match_id)
    # )
    # res_debug = (await session.execute(stmt_debug)).fetchall()
    # if res_debug[0] == res_debug[1]:
    #     response.status_code = HTTP_400_BAD_REQUEST
    #     await session.rollback()
    #     return {"can't be 2 similar team in 1 match"}
    await session.commit()
