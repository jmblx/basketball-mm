import os

from sqlalchemy import select
import shutil
from PIL import Image

from database import async_session_maker


# Базовая функция для сбора данных с БД
async def get_data(
    class_,
    filter,
    is_scalar: bool = False,
    order_by=None
):
    async with async_session_maker() as session:
        stmt = select(class_).where(filter)
        if is_scalar:
            res_query = await session.execute(stmt)
            res = res_query.scalar()
        else:
            if order_by:
                stmt = select(class_).where(filter).order_by(order_by)
            res_query = await session.execute(stmt)
            res = res_query.fetchall()
            res = [result[0] for result in res]
    return res


async def create_upload_avatar(
    object_id: int,
    file,
    class_,
    path: str,
):
    async with async_session_maker() as session:
        object = await session.get(class_, object_id)
        save_path = os.path.join(path, f"object{object.id}{file.filename}")

        with open(save_path, "wb") as new_file:
            shutil.copyfileobj(file.file, new_file)

        with Image.open(save_path) as img:
            img.thumbnail((350, 350))
            img.save(save_path)

        object.pathfile = save_path
        await session.commit()

    return save_path
