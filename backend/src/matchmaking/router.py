from datetime import datetime
import json
from uuid import UUID

from fastapi import (
    APIRouter, Request, WebSocket,
    WebSocketDisconnect, Depends, BackgroundTasks
)
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from database import get_async_session, async_session_maker
from redis_config import get_redis
from tournaments.models import StatusEvent, SoloMatch

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/finding-match/1x1", tags=["matchmaking"])


async def notify_user_about_match(player_ids, match_id):
    for player_id in player_ids:
        player_id = str(player_id)
        if player_id in connected_users:
            await connected_users[player_id].send_text(
                json.dumps({"action": "matchFound", "matchId": match_id})
            )


connected_users = {}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, userid):
    await websocket.accept()
    connected_users[userid] = websocket
    try:
        while True:
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        del connected_users[userid]


async def add_user_to_search(
    user_id: UUID,
    user_rating: int,
    redis
):
    await redis.zadd('user_search_queue', {str(user_id): user_rating})


async def remove_user_from_search(user_id: str, redis):
    await redis.zrem('user_search_queue', str(user_id))


async def find_opponent(user_id: UUID, user_rating: int, threshold: int, redis):
    opponents = await redis.zrangebyscore(
        'user_search_queue',
        user_rating - threshold,
        user_rating + threshold,
        withscores=True
    )
    for opponent_id, opponent_rating in opponents:
        if str(opponent_id) != str(user_id):

            print(f"chel {user_id} | opp {opponent_id}")
            return opponent_id, opponent_rating
    return None, None


@router.post("/start_search/{user_id}")
async def start_search(
    user_id: UUID,
    background_tasks: BackgroundTasks,
    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.get(User, user_id)
    await add_user_to_search(user_id, user.solo_rating, redis)
    background_tasks.add_task(search_for_match, user_id, user.solo_rating, redis)
    return {"message": "Search started"}


@router.post("/stop_search/{user_id}")
async def stop_search(user_id: UUID, redis=Depends(get_redis)):
    await remove_user_from_search(str(user_id), redis)
    return {"message": "Search stopped"}


async def search_for_match(user_id, user_rating, redis):
    opponent_id, _ = await find_opponent(user_id, user_rating, 100, redis)
    if opponent_id:
        match_id, player_ids = await create_potential_match(user_id, opponent_id, redis)
        await notify_user_about_match(player_ids, match_id)


async def create_potential_match(user1_id: int, user2_id: int, redis):
    async with async_session_maker() as session:
        player_ids = [user1_id, user2_id]
        user1 = await session.get(User, user1_id)
        user2 = await session.get(User, user2_id)
        match = SoloMatch(players=[user1, user2], start_date=datetime.utcnow())
        session.add(match)
        await session.commit()
        await redis.sadd(f"solomatch:{match.id}:user1", str(user1_id))
        await redis.sadd(f"solomatch:{match.id}:user2", str(user2_id))
        await redis.hmset(f"solomatch:{match.id}", {'user1_id': str(user1_id), 'user2_id': str(user2_id), 'status': 'pending'})
        return match.id, player_ids


async def finalize_match(match_id: int, redis):
    async with async_session_maker() as session:
        match = (await session.execute(
            select(SoloMatch).options(selectinload(SoloMatch.players)).where(SoloMatch.id == match_id)
        )).unique().scalar_one()
        match.status = StatusEvent.pending
        session.add(match)
        await session.commit()
        user1_id = match.players[0].id
        user2_id = match.players[1].id
        await redis.zrem('user_search_queue', str(user1_id))
        await redis.zrem('user_search_queue', str(user2_id))
        await redis.delete(f"solomatch:{match_id}")
        await redis.delete(f"solomatch:{match_id}")
        await redis.delete(f"solomatch:{match_id}:user1")
        await redis.delete(f"solomatch:{match_id}:user2")
        await redis.delete(f"solomatch:{match_id}:confirmed_players")
        await notify_user(str(user1_id), "matchStarted", "match started")
        await notify_user(str(user2_id), "matchStarted", "match started")


@router.post("/confirm_ready/{match_id}/{player_id}")
async def confirm_ready(match_id: int, player_id: UUID, redis=Depends(get_redis)):
    player_id_str = str(player_id)
    is_user1 = await redis.sismember(f"solomatch:{match_id}:user1", player_id_str)
    is_user2 = await redis.sismember(f"solomatch:{match_id}:user2", player_id_str)

    if not (is_user1 or is_user2):
        return {"status": "not in match"}

    is_confirmed = await redis.sismember(f"solomatch:{match_id}:confirmed_players", player_id_str)
    if is_confirmed:
        return {"status": "already confirmed"}
    await redis.sadd(f"solomatch:{match_id}:confirmed_players", player_id_str)
    confirmed_players = await redis.scard(f"solomatch:{match_id}:confirmed_players")

    if confirmed_players == 2:
        await finalize_match(match_id, redis)

    return {"status": "confirmed"}


async def notify_user(user_id, action, message):
    await connected_users[user_id].send_text(json.dumps({"action": action, "message": message}))


@router.post("/not_ready/{match_id}/{user_id}")
async def not_ready(
    match_id: int,
    user_id: UUID,

    redis=Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
):
    match = (await session.execute(
        select(SoloMatch).options(selectinload(SoloMatch.players)).where(SoloMatch.id == match_id)
    )).unique().scalar_one()
    if match:
        match.status = StatusEvent.cancelled
        session.add(match)
        await session.commit()
    opposing_user_id = match.players[0].id if user_id != match.players[0].id else match.players[1].id
    opposing_user = await session.get(User, opposing_user_id)
    await redis.delete(f"solomatch:{match_id}:confirmed_players")
    await redis.delete(f"solomatch:{match_id}:players")

    await redis.zrem('user_search_queue', str(user_id))
    await redis.zrem('user_search_queue', str(opposing_user_id))
    await notify_user(str(user_id), "matchCancelled", "Match cancelled by you.")
    await notify_user(str(opposing_user_id), "matchResearch", "Match cancelled by your opp. Searching for a new match.")
    if opposing_user:
        await add_user_to_search(opposing_user_id, opposing_user.solo_rating, redis)
        await search_for_match(opposing_user_id, opposing_user.solo_rating, redis)
    return {"status": "search restarted for opposing user"}


@router.get("/")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("search_solo.html", {"request": request})
