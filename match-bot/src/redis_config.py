from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis.asyncio.utils import from_url


class RedisSession(BaseMiddleware):
    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        redis = await from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        try:
            data['redis'] = redis
            response = await handler(event, data)
        finally:
            await redis.close()
        return response
