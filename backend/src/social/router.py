import fastapi
from fastapi import Depends
from sqlalchemy import func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from auth.models import User, Team
from database import get_async_session
from utils import change_layout, find_object

router = fastapi.APIRouter(prefix="/social", tags=["social"])


@router.get("/find-user")
async def find_user(
    nickname: str,
):
    result = await find_object(User, User.nickname, nickname, 0.3)
    return result


@router.get("/find-team")
async def find_team(
    team_name: str,
):
    result = await find_object(Team, Team.name, team_name, 0.3)
    return result
