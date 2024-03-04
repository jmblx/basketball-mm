import base64
import os
import random
from uuid import UUID

import fastapi
from fastapi import Depends, UploadFile, Request
from fastapi.responses import FileResponse
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from auth.base_config import current_user
from auth.models import User, Role, Team, UserTeam
from auth.schemas import RoleSchema
from constants import IMAGES_DIR
from database import get_async_session
from matchmaking.router import templates
from utils import create_upload_avatar, get_user_attrs, team_to_dict

router = fastapi.APIRouter(prefix="/profile", tags=["user-profile"])


@router.get("/")
async def get_user_data(
    user: User = Depends(current_user),
):
    return await get_user_attrs(user)


@router.get("/img-page")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("img.html", {"request": request})


@router.post("/uploadfile/user/avatar")
async def upload_user_avatar(
    file: UploadFile,
    user: User = Depends(current_user)
):
    class_ = User
    user_avatar_dir = os.path.join(IMAGES_DIR, "user")
    res = await create_upload_avatar(user.id, file, class_, user_avatar_dir)
    return res


@router.get("/image/{user_id}")
async def get_image(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.get(User, user_id)
    return FileResponse(user.pathfile)


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


@router.get("/user-teams")
async def get_user_team(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    user_with_teams: User = ((await session.execute(
        select(User).options(joinedload(User.teams))
        .filter(User.id == user_id)))
        .unique().first())[0]
    result = {f"team{num}": await team_to_dict(team) for num, team in enumerate(user_with_teams.teams)}
    return result


@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    users_teams = (await session.execute(
        select(Team).options(selectinload(Team.players)).where(Team.captain_id == user_id)
    )).scalars().all()
    await session.execute(delete(UserTeam).where(UserTeam.user_id == user_id))
    for team in users_teams:
        print(team.name)
        if len(team.players) > 0:
            # Исключаем удаляемого капитана из списка возможных новых капитанов
            possible_new_captains = [player for player in team.players if player.id != user_id]
            if possible_new_captains:
                # Выбираем случайного нового капитана
                new_captain = random.choice(possible_new_captains)
                # Обновляем команду с новым капитаном
                await session.execute(
                    update(Team).where(Team.id == team.id).values(captain_id=new_captain.id)
                )
            else:
                # Если в команде не осталось других участников, можно установить captain_id в None или предпринять другие действия
                # await session.execute(
                #     update(Team).where(Team.id == team.id).values(captain_id=None, number=team.number-1)
                # )
                await session.execute(
                    delete(Team).where(Team.id == team.id)
                )
    await session.execute(delete(User).where(User.id == user_id))
    await session.commit()

    return {"message": "User deleted and new captains assigned where applicable"}
