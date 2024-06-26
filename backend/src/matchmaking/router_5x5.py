import asyncio
from datetime import datetime
import json
from uuid import UUID

from fastapi import (
    APIRouter,
    FastAPI,
    Request,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    BackgroundTasks,
)
from fastapi.templating import Jinja2Templates
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from auth.models import Team
from database import get_async_session, async_session_maker
from redis_config import get_redis
from tournaments.models import Match5x5, StatusEvent

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/finding-match/5x5", tags=["matchmaking"])


async def notify_teams_about_match(player_ids, match_id):
    print(f"Дебилы: {player_ids}")
    print(f"Законнекченные: {connected_users}")
    msg = "matchFound5x5Cap" if len(player_ids) == 2 else "matchFound5x5Mem"
    for player_id in player_ids:
        if player_id in connected_users:
            print(f"message sent to {player_id}")
            await connected_users[player_id].send_text(
                json.dumps({"action": msg, "matchId": match_id})
            )


connected_users = {}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, userid: UUID, teamid: int, redis=Depends(get_redis)
):
    await websocket.accept()
    connected_users[userid] = websocket
    print(connected_users)
    try:
        while True:
            data = await websocket.receive_text()

    except WebSocketDisconnect:

        await redis.zrem("team_search_queue", str(teamid))

        del connected_users[userid]


async def add_team_to_search(team_id: int, team_rating: int, redis):
    await redis.zadd("team_search_queue", {str(team_id): team_rating})


async def remove_team_from_search(team_id: str, redis):
    await redis.zrem("team_search_queue", team_id)


async def find_opponent(team_id: int, team_rating: int, threshold: int, redis):
    opponents = await redis.zrangebyscore(
        "team_search_queue",
        team_rating - threshold,
        team_rating + threshold,
        withscores=True,
    )
    for opponent_id, opponent_rating in opponents:
        print(int(opponent_id), opponent_rating)
        if int(opponent_id) != team_id:
            return int(opponent_id), int(opponent_rating)
    return None, None


@router.post("/start_search/{team_id}")
async def start_search(
    team_id: int,
    background_tasks: BackgroundTasks,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    team = (
        (
            await session.execute(
                select(Team)
                .options(joinedload(Team.players))
                .where(Team.id == team_id)
            )
        )
        .unique()
        .scalar_one()
    )
    await add_team_to_search(team_id, team.rating_5x5, redis)
    background_tasks.add_task(
        search_for_match, team_id, team.rating_5x5, redis
    )
    print(f" команда {team_id}")
    return {"message": "Search started"}


@router.post("/stop_search/{team_id}")
async def stop_search(team_id: int, redis=Depends(get_redis)):
    await remove_team_from_search(str(team_id), redis)
    return {"message": "Search stopped"}


async def search_for_match(team_id, team_rating, redis):
    opponent_id, _ = await find_opponent(team_id, team_rating, 100, redis)
    # print(f"opp: {opponent_id}")
    if opponent_id:
        match_id, player_ids = await create_potential_match(
            team_id, opponent_id, redis
        )
        await notify_teams_about_match(player_ids, match_id)


async def create_potential_match(team1_id: int, team2_id: int, redis):
    async with async_session_maker() as session:
        result = (
            await session.execute(
                select(Team)
                .options(joinedload(Team.players))
                .where(Team.id.in_([team1_id, team2_id]))
            )
        ).unique()
        teams = result.scalars().all()
        team1, team2 = teams
        team1_player_ids = [player.id for player in team1.players]
        team2_player_ids = [player.id for player in team2.players]
        player_ids = team1_player_ids + team2_player_ids
        team1_player_ids = list(
            map(lambda plyer_id: str(plyer_id), team1_player_ids)
        )
        team2_player_ids = list(
            map(lambda plyer_id: str(plyer_id), team2_player_ids)
        )
        match = Match5x5(teams=[team1, team2], start_date=datetime.utcnow())
        session.add(match)
        await session.commit()
        match_id = match.id
        await redis.sadd(f"match:{match_id}:team1", *team1_player_ids)
        await redis.sadd(f"match:{match_id}:team2", *team2_player_ids)
        await redis.hmset(
            f"match:{match_id}",
            {"team1_id": team1_id, "team2_id": team2_id, "status": "pending"},
        )
        return match_id, player_ids


async def finalize_match(match_id, redis):
    async with async_session_maker() as session:
        match = (
            (
                await session.execute(
                    select(Match5x5)
                    .options(selectinload(Match5x5.teams))
                    .where(Match5x5.id == match_id)
                )
            )
            .unique()
            .scalar_one()
        )
        match.status = StatusEvent.pending
        session.add(match)
        await session.commit()
        await redis.zrem("team_search_queue", str(match.teams[0].id))
        await redis.zrem("team_search_queue", str(match.teams[1].id))
    await redis.delete(f"match:{match_id}")
    await redis.delete(f"match:{match_id}:team1")
    await redis.delete(f"match:{match_id}:team2")
    await redis.delete(f"match:{match_id}:confirmed_players")


@router.post("/player/confirm_ready/{match_id}/{player_id}")
async def confirm_ready_player(
    match_id: int,
    player_id: UUID,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    player_id_str = str(player_id)
    is_team1_member = await redis.sismember(
        f"match:{match_id}:team1", player_id_str
    )
    is_team2_member = await redis.sismember(
        f"match:{match_id}:team2", player_id_str
    )

    if not (is_team1_member or is_team2_member):
        return {"status": "not in match"}

    is_confirmed = await redis.sismember(
        f"match:{match_id}:confirmed_players", player_id_str
    )
    if is_confirmed:
        return {"status": "already confirmed"}
    await redis.sadd(f"match:{match_id}:confirmed_players", player_id_str)
    print(player_id_str)
    total_players = await redis.scard(
        f"match:{match_id}:team1"
    ) + await redis.scard(f"match:{match_id}:team2")
    confirmed_players = await redis.scard(
        f"match:{match_id}:confirmed_players"
    )

    if confirmed_players == total_players:
        match = (
            (
                await session.execute(
                    select(Match5x5)
                    .options(selectinload(Match5x5.teams))
                    .where(Match5x5.id == match_id)
                )
            )
            .unique()
            .scalar_one()
        )
        await notify_team(
            match.teams[0].id, "matchStarted", f"Match {match_id} is starting"
        )
        await notify_team(
            match.teams[1].id, "matchStarted", f"Match {match_id} is starting"
        )
        await finalize_match(match_id, redis)

    return {"status": "confirmed"}


async def notify_team(team_id, action, message):
    async with async_session_maker() as session:
        team = (
            (
                await session.execute(
                    select(Team)
                    .options(joinedload(Team.players))
                    .where(Team.id == team_id)
                )
            )
            .unique()
            .scalar_one()
        )
        for player in team.players:
            print(player.id)
            if player.id in connected_users:
                await connected_users[player.id].send_text(
                    json.dumps({"action": action, "message": message})
                )
                print(player.id)
    print(connected_users)

    print(action)


@router.post("/player/not_ready/{match_id}/{team_id}")
async def not_ready_player(
    match_id: int,
    team_id: int,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    match = (
        (
            await session.execute(
                select(Match5x5)
                .options(selectinload(Match5x5.teams))
                .where(Match5x5.id == match_id)
            )
        )
        .unique()
        .scalar_one()
    )
    if match:
        match.status = StatusEvent.cancelled
        session.add(match)
        await session.commit()
    opposing_team_id = (
        match.teams[0].id
        if team_id != match.teams[0].id
        else match.teams[1].id
    )
    opposing_team = await session.get(Team, opposing_team_id)
    await redis.delete(f"match:{match_id}:confirmed_players")
    await redis.delete(f"match:{match_id}:players")

    await redis.zrem("team_search_queue", str(team_id))
    await redis.zrem("team_search_queue", str(opposing_team_id))
    print(opposing_team_id)
    await notify_team(
        team_id, "matchCancelled", "Match cancelled by your team."
    )
    await notify_team(
        opposing_team_id,
        "matchResearch",
        "Match cancelled by opposing team. Searching for a new match.",
    )
    if opposing_team:
        await add_team_to_search(
            opposing_team_id, opposing_team.rating_5x5, redis
        )
        await search_for_match(
            opposing_team_id, opposing_team.rating_5x5, redis
        )
    return {"status": "search restarted for opposing team"}


@router.post("/captain/confirm_ready/{match_id}/{team_id}")
async def confirm_ready(
    match_id: int,
    team_id: int,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    team_id_str = str(team_id)

    await redis.sadd(f"match:{match_id}:confirmed_teams", team_id_str)
    confirmed_players = await redis.scard(f"match:{match_id}:confirmed_teams")

    if confirmed_players == 2:
        match = (
            (
                await session.execute(
                    select(Match5x5)
                    .options(selectinload(Match5x5.teams))
                    .where(Match5x5.id == match_id)
                )
            )
            .unique()
            .scalar_one()
        )
        await notify_team(
            match.teams[0].id, "matchStarted", f"Match {match_id} is starting"
        )
        await notify_team(
            match.teams[1].id, "matchStarted", f"Match {match_id} is starting"
        )
        await finalize_match(match_id, redis)

    return {"status": "confirmed"}


@router.post("/captain/not_ready/{match_id}/{team_id}")
async def not_ready(
    match_id: int,
    team_id: int,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    match = (
        (
            await session.execute(
                select(Match5x5)
                .options(selectinload(Match5x5.teams))
                .where(Match5x5.id == match_id)
            )
        )
        .unique()
        .scalar_one()
    )
    if match:
        match.status = StatusEvent.cancelled
        session.add(match)
        await session.commit()
    opposing_team_id = (
        match.teams[0].id
        if team_id != match.teams[0].id
        else match.teams[1].id
    )
    opposing_team = await session.get(Team, opposing_team_id)
    await redis.delete(f"match:{match_id}:confirmed_teams")
    await redis.delete(f"match:{match_id}:players")

    await redis.zrem("team_search_queue", str(team_id))
    await redis.zrem("team_search_queue", str(opposing_team_id))
    print(opposing_team_id)
    await notify_team(
        team_id, "matchCancelled", "Match cancelled by your team's captain."
    )
    await notify_team(
        opposing_team_id,
        "matchResearch",
        "Match cancelled by opposing team's captain. Searching for a new match.",
    )
    if opposing_team:
        await add_team_to_search(
            opposing_team_id, opposing_team.rating_5x5, redis
        )
        await search_for_match(
            opposing_team_id, opposing_team.rating_5x5, redis
        )
    return {"status": "search restarted for opposing team"}


@router.get("/")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("5x5.html", {"request": request})
