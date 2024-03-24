import redis.asyncio as aioredis

from config import REDIS_HOST, REDIS_PORT


async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    try:
        yield redis
    finally:
        await redis.close()
