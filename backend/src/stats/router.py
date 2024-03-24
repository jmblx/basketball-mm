import fastapi
from fastapi import Depends
from fastapi_cache.decorator import cache
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session

router = fastapi.APIRouter(prefix="/stats", tags=["stats"])


@router.get("/top5-users-solo")
# @cache(expire=30)
async def get_top5_user_solo(
    session: AsyncSession = Depends(get_async_session),
):
    top5 = (
        (
            await session.execute(
                select(User).order_by(desc(User.solo_rating)).limit(5)
            )
        )
        .unique()
        .all()
    )
    top5 = [user[0] for user in top5]
    result = {f"top{i+1}": user_to_dict(user) for i, user in enumerate(top5)}
    return result


def user_to_dict(user: User):
    return {
        "id": user.id,
        "nickname": user.nickname,
        "solo_rating": user.solo_rating,
        "solomatch_winrate": user.solomatch_winrate,
    }
