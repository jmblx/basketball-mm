import json

import fastapi
from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session
from matchmaking.schemas import SetSoloMatchResult, Message
from producer import AIOWebProducer, get_producer
from redis_config import get_redis
from tournaments.models import SoloMatch
from utils import get_match_data

router = fastapi.APIRouter(prefix="/solomatch", tags=["matchmaking"])


@router.put("/set-match-result")
async def set_solomatch_result(
    match_id: int,
    match_result: SetSoloMatchResult,
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
    producer: AIOWebProducer = Depends(get_producer),
):
    first_player_id = match_result.first_player_result.id
    first_player_score = match_result.first_player_result.score
    second_player_id = match_result.second_player_result.id
    second_player_score = match_result.second_player_result.score

    winner_id = (
        first_player_id
        if first_player_score > second_player_score
        else second_player_id
    )
    loser_id = (
        first_player_id
        if first_player_score < second_player_score
        else second_player_id
    )

    await session.execute(
        update(SoloMatch)
        .where(SoloMatch.id == match_id)
        .values(
            {
                "winner_id": winner_id,
                "scores": {
                    "first_player": {
                        "id": str(first_player_id),
                        "score": first_player_score,
                    },
                    "second_player": {
                        "id": str(second_player_id),
                        "score": second_player_score,
                    },
                },
            }
        )
    )

    winner = await session.get(User, winner_id)
    loser = await session.get(User, loser_id)

    winner_wins = winner.solomatch_wins + 1
    winner_winrate = winner_wins / (winner_wins + winner.solomatch_loses) * 100
    await session.execute(
        update(User)
        .where(User.id == winner_id)
        .values(solomatch_wins=winner_wins, solomatch_winrate=winner_winrate)
    )

    loser_loses = loser.solomatch_loses + 1
    loser_winrate = (
        loser.solomatch_wins / (loser.solomatch_wins + loser_loses) * 100
    )
    await session.execute(
        update(User)
        .where(User.id == loser_id)
        .values(solomatch_loses=loser_loses, solomatch_winrate=loser_winrate)
    )
    await session.commit()
    if await redis.smembers(f"auth:{winner.tg_id}"):
        winner_message = {
            str(winner.tg_id): Message(
                match_type="1x1",
                match_result="win",
                solo_rating_change=0,
                current_solo_rating=winner.solo_rating,
                opponent_nickname=loser.nickname,
            )
        }
        message_to_produce = json.dumps(winner_message.model_dump()).encode(
            encoding="utf-8"
        )
        await producer.send(value=message_to_produce)
    if await redis.smembers(f"auth:{loser.tg_id}"):
        loser_message = {
            str(loser.tg_id): Message(
                match_type="1x1",
                match_result="lose",
                solo_rating_change=0,
                current_solo_rating=loser.solo_rating,
                opponent_nickname=winner.nickname,
                telegram_id=int(loser.tg_id)
            )
        }
        message_to_produce = json.dumps(loser_message.model_dump()).encode(
            encoding="utf-8"
        )
        await producer.send(value=message_to_produce)
    match = await session.get(SoloMatch, match_id)

    return {
        "details": f"now in match with id = {match_id} winner is {winner_id} and it's status={match.status}"
    }


@router.get("/{match_id}")
async def get_solomatch(match_id: int):
    data = await get_match_data(SoloMatch, match_id)
    return {"data": data}
