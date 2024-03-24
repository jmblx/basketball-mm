# import aiofiles
import os
import zipfile
import io
from typing import Any, Dict

from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import select, text, or_, func, update, exc
import shutil
from PIL import Image
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import selectinload

from auth.models import User, Team
from database import async_session_maker
from tournaments.models import Match5x5, SoloMatch


# Базовая функция для сбора данных с БД
async def get_data(class_, filter, is_scalar: bool = False, order_by=None):
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
    object_id,
    file,
    class_,
    path: str,
):
    async with async_session_maker() as session:
        object = await session.get(class_, object_id)
        save_path = os.path.join(path, f"object{object.id}{file.filename}")

        with open(save_path, "wb") as new_file:
            shutil.copyfileobj(file.file, new_file)

        # Открываем изображение
        with Image.open(save_path) as img:
            # Изменяем размер изображения на 350x350
            img = img.resize((350, 350))
            # Создаем новый файл, преобразовывая изображение в формат WebP
            new_save_path = os.path.splitext(save_path)[0] + ".webp"
            img.save(new_save_path, "WEBP")

        # Удаляем старый файл
        os.remove(save_path)

        # Обновляем путь к файлу в объекте
        object.pathfile = new_save_path
        await session.commit()

    return new_save_path


# async def get_images_for_objects(
#     object_ids: List[int],
#     class_: Any,
#     session: AsyncSession
# ):
#     images = []
#     for object_id in object_ids:
#         obj = await session.get(class_, object_id)
#         if not obj:
#             raise HTTPException(status_code=404, detail=f"{class_.__name__} with ID {object_id} not found")
#         images.append(await aiofiles.open(obj.pathfile, mode='rb'))  # Открываем файл в бинарном режиме и добавляем его в список
#     return images


async def generate_zip_archive(files):
    in_memory_output = io.BytesIO()
    with zipfile.ZipFile(in_memory_output, mode="w") as zf:
        for i, file in enumerate(files):
            content = await file.read()  # Читаем содержимое файла
            zf.writestr(
                f"image_{i}.webp", content
            )  # Записываем содержимое в ZIP-архив
    in_memory_output.seek(0)
    return StreamingResponse(
        io.BytesIO(in_memory_output.read()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=images.zip"},
    )


def recalculate_winrate(user: User):
    return (
        user.solomatch_wins
        / (user.solomatch_wins + user.solomatch_loses)
        * 100
    )


def change_layout(text):
    conversion = {
        "q": "й",
        "w": "ц",
        "e": "у",
        "r": "к",
        "t": "е",
        "y": "н",
        "u": "г",
        "i": "ш",
        "o": "щ",
        "p": "з",
        "[": "х",
        "]": "ъ",
        "a": "ф",
        "s": "ы",
        "d": "в",
        "f": "а",
        "g": "п",
        "h": "р",
        "j": "о",
        "k": "л",
        "l": "д",
        ";": "ж",
        "'": "э",
        "z": "я",
        "x": "ч",
        "c": "с",
        "v": "м",
        "b": "и",
        "n": "т",
        "m": "ь",
        ",": "б",
        ".": "ю",
        "`": "ё",
        "й": "q",
        "ц": "w",
        "у": "e",
        "к": "r",
        "е": "t",
        "н": "y",
        "г": "u",
        "ш": "i",
        "щ": "o",
        "з": "p",
        "х": "[",
        "ъ": "]",
        "ф": "a",
        "ы": "s",
        "в": "d",
        "а": "f",
        "п": "g",
        "р": "h",
        "о": "j",
        "л": "k",
        "д": "l",
        "ж": ";",
        "э": "'",
        "я": "z",
        "ч": "x",
        "с": "c",
        "м": "v",
        "и": "b",
        "т": "n",
        "ь": "m",
        "б": ",",
        "ю": ".",
        "ё": "`",
    }

    return "".join([conversion.get(char, char) for char in text])


async def find_object(
    entity_class, entity_parameter, entity_mark: str, similarity: float = 0.3
):
    async with async_session_maker() as session:
        await session.execute(
            text(f"SET pg_trgm.similarity_threshold = {similarity};")
        )
        entity_converted = change_layout(entity_mark)
        query = select(entity_class).where(
            or_(
                func.similarity(entity_parameter, entity_mark) > 0.3,
                func.similarity(entity_parameter, entity_converted) > 0.3,
            )
        )
        result = (await session.execute(query)).unique().fetchall()

        if entity_class != Team:
            result = [
                getattr(entity[0], entity_parameter.name) for entity in result
            ]
        else:
            result = [
                {"name": team[0].name, "slug": team[0].slug} for team in result
            ]

        return result if result else {"result": "not found"}


async def get_user_attrs(user: User):
    return {
        "nickname": user.nickname,
        "registered_at": user.registered_at,
        "id": user.id,
        "rating": user.solo_rating,
        "group_rating": user.rating_5x5,
        "details": None,
    }


async def team_to_dict(team: Team):
    return {
        "team_id": team.id,
        "name": team.name,
        "number": team.number,
        "captain_id": team.captain_id,
        "is_captain_only_search": team.is_captain_only_search,
        "rating_5x5": team.rating_5x5,
        "loses": team.match5x5_loses,
        "wins": team.match5x5_wins,
        "winrate": team.match5x5_winrate,
    }


async def get_object_images(
    class_: Any,
    object_ids: str,
):
    async with async_session_maker() as session:
        object_ids = object_ids.split(",")
        object_ids = list(map(lambda x: int(x), object_ids))
        images = {
            f"{(class_.__name__).lower()}{object_id}": (
                await session.get(class_, object_id)
            ).pathfile
            for object_id in object_ids
        }
        return images


async def get_user_card_info(user_id: int):
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        return {
            "rating5x5": user.rating_5x5,
            "nickname": user.nickname,
            "image": user.pathfile,
        }


async def get_team_card_info(team_id: int):
    async with async_session_maker() as session:
        team = await session.get(Team, team_id)
        return {
            "rating5x5": team.rating_5x5,
            "name": team.name,
            "image": team.pathfile,
        }


def create_team_data(
    team, opponent_team, match_result, player_score, opponent_score
):
    return {
        "match_type": "5x5",
        "team_name": team.name,
        "opp_team_name": opponent_team.name,
        "team_players": [player.nickname for player in team.players],
        "opp_team_players": [
            player.nickname for player in opponent_team.players
        ],
        "team_score": player_score,
        "opp_team_score": opponent_score,
        "match_result": match_result,
    }


async def prepare_data_mailing(
    player, team, opponent_team, result, score, opponent_score, redis
) -> Dict:
    if await redis.smembers(f"auth:{player.tg_id}"):
        return {
            str(player.tg_id): create_team_data(
                team, opponent_team, result, score, opponent_score
            )
        }
    return {}


async def update_object(
    data: BaseModel,
    class_,
    obj_id: int,
    if_slug: bool = False,
    attr_name: str = "name",
) -> None:
    async with async_session_maker() as session:
        update_data = {
            key: value
            for key, value in data.model_dump().items()
            if value is not None
        }
        if if_slug:
            update_data["slug"] = slugify(
                update_data.get(attr_name), lowercase=True
            )
        try:
            await session.execute(
                update(class_).where(class_.id == obj_id).values(update_data)
            )
            await session.commit()
        except exc.IntegrityError:
            await session.rollback()
            update_data["slug"] = f'{update_data["slug"]}-{obj_id}'
            await session.execute(
                update(class_).where(class_.id == obj_id).values(update_data)
            )
            await session.commit()


async def get_match_data(class_, obj_id: int):
    async with async_session_maker() as session:

        if class_ == SoloMatch:
            match = (await session.get(class_, obj_id))
            first_player = await session.get(User, match.scores.get("first_player").get("id"))
            second_player = await session.get(User, match.scores.get("second_player").get("id"))
            return {
                "first_player_id": first_player.id,
                "first_player_score": match.scores.get("first_player").get("score"),
                "first_player_nickname": first_player.nickname,
                "first_player_image": first_player.pathfile,
                "second_player_id": second_player.id,
                "second_player_score": match.scores.get("second_player").get("score"),
                "second_player_nickname": second_player.nickname,
                "second_player_image": second_player.pathfile,
                "match_status": match.status,
            }
        if class_ == Match5x5:
            match = (await session.get(class_, obj_id))
            first_team = await session.get(Team, match.scores.get("team1").get("team_id"))
            second_team = await session.get(Team, match.scores.get("team2").get("team_id"))
            return {
                "first_team_id": first_team.id,
                "first_team_score": match.scores.get("first_team_score"),
                "first_team_name": first_team.name,
                "first_team_image": first_team.pathfile,
                "second_team_id": second_team.id,
                "second_team_score": match.scores.get("second_team_score"),
                "second_team_name": second_team.name,
                "second_team_image": second_team.pathfile,
                "match_status": match.status,
            }
        #if class_ == Match:
        return Exception("Unknown match class")
