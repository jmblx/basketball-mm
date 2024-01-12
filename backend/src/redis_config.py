import redis.asyncio as aioredis

async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()
