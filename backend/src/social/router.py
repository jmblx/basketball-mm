import fastapi
from fastapi import Depends
from sqlalchemy import func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from auth.models import User
from database import get_async_session
from utils import change_layout

router = fastapi.APIRouter(prefix="/social", tags=["social"])

@router.get("/find-user")
async def find_user(
    nickname: str,
    session: AsyncSession = Depends(get_async_session)
):
    await session.execute(text("SET pg_trgm.similarity_threshold = 0.5;"))
    nickname_converted = change_layout(nickname)

    query = select(User).where(
        or_(
            func.similarity(User.nickname, nickname) > 0.3,
            func.similarity(User.nickname, nickname_converted) > 0.3
        )
    )
    result = (await session.execute(query)).unique().fetchall()
    nicknames = [user[0].nickname for user in result]
    print(nicknames)
    return nicknames if nicknames else {"result": "not found"}

