import fastapi
from fastapi import Depends, UploadFile
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User, Role
from auth.schemas import RoleSchema
from constants import images_dir
from database import get_async_session
from utils import create_upload_avatar

router = fastapi.APIRouter(prefix="/profile", tags=["user-profile"])


@router.get("/")
async def get_user_data(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return {
        "status": "success",
        "nickname": user.nickname,
        "registered_at": user.registered_at,
        "id": user.id,
        "rating": user.solo_rating,
        "details": None
    }


@router.post("/uploadfile/user/avatar")
async def upload_user_avatar(
    file: UploadFile,
    user_id: int,
):
    class_ = User
    user_avatar_dir = f"{images_dir}\\user"
    res = await create_upload_avatar(user_id, file, class_, user_avatar_dir)
    return res


@router.post("/add-role")
async def add_role(
    role: RoleSchema,
    session: AsyncSession = Depends(get_async_session),
    # user: User = Depends(current_user)
):
    stmt = insert(Role).values(**role.model_dump())
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}
