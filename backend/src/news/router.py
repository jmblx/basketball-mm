import os
import random

import fastapi
from fastapi import Depends, HTTPException, Response, UploadFile
from slugify import slugify
from sqlalchemy import exc, update, insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from constants import IMAGES_DIR
from database import get_async_session
from news.models import News, NewsCategory
from news.schemas import AddNews, UpdateNews, AddCategory, UpdateCategory
from utils import create_upload_avatar, update_object

router = fastapi.APIRouter(prefix="/news", tags=["news"])


@router.post("/add")
async def add_news(data: AddNews, session: AsyncSession = Depends(get_async_session)):
    news_data = data.model_dump()
    original_slug = slugify(news_data["title"], lowercase=True)
    news_data["slug"] = original_slug
    suffix = 0
    while True:
        if suffix > 0:
            news_data["slug"] = f'{original_slug}-{suffix}'
        try:
            stmt = insert(News).values(news_data)
            await session.execute(stmt)
            await session.commit()
            break
        except exc.IntegrityError:
            await session.rollback()
            suffix += 1


@router.put("/update/{news_id}")
async def update_news(
    news_id: int,
    data: UpdateNews,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    # update_data = {key: value for key, value in data.model_dump().items() if value is not None}
    # if "name" in update_data.keys():
    #     update_data["slug"] = slugify(update_data.get("name"), lowercase=True)
    # try:
    #     await session.execute(update(News).where(News.id == news_id).values(update_data))
    #     await session.commit()
    # except exc.IntegrityError:
    #     await session.rollback()
    #     update_data["slug"] = f'{update_data["slug"]}-{news_id}'
    #     await session.execute(update(News).where(News.id == news_id).values(update_data))
    #     await session.commit()
    await update_object(data, class_=News, obj_id=news_id, if_slug=True, attr_name="title")
    return {"status": "successful update"}


@router.post("/set_image/{news_id}")
async def upload_team_avatar(
    file: UploadFile,
    news_id: int,
):
    class_ = News
    team_avatar_dir = os.path.join(IMAGES_DIR, "news")

    res = await create_upload_avatar(news_id, file, class_, team_avatar_dir)
    return res


@router.delete("/delete/{news_id}")
async def delete_news(
    news_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        delete(News).where(News.id == news_id)
    )
    await session.execute(stmt)
    await session.commit()
    return {"status": "successful delete"}


@router.post("/add/category")
async def add_category(
    data: AddCategory,
    session: AsyncSession = Depends(get_async_session),
):
    cat = NewsCategory(**data.model_dump())
    cat.slug = slugify(cat.name, lowercase=True)
    session.add(cat)
    await session.commit()


@router.put("/update/category/{cat_id}")
async def add_category(
    cat_id: int,
    data: UpdateCategory,
    session: AsyncSession = Depends(get_async_session),
):
    await update_object(data, class_=NewsCategory, obj_id=cat_id, if_slug=True, attr_name="name")
    return {"status": "successful update"}
