from sqlalchemy import and_, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Recipe


async def orm_add_recipe(session: AsyncSession, data: dict):
    obj = Recipe(**data)
    session.add(obj)
    await session.commit()


async def orm_get_recipes(session: AsyncSession):
    query = select(Recipe)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, recipe_id: int):
    query = select(Recipe).where(Recipe.id == recipe_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_random_recipe(session: AsyncSession, is_cocktail: bool):
    try:
        query = select(Recipe).where(and_(Recipe.is_cocktail == is_cocktail, Recipe.is_showed == False)).order_by(func.random()).limit(1)
        result = await session.execute(query)
        cocktail = result.scalars().first()
        if cocktail is None:
            await session.execute(update(Recipe).where(Recipe.is_cocktail == is_cocktail).values(is_showed=False))
            await session.commit()
            result = await session.execute(query)
            cocktail = result.scalars().first()
        print((await session.execute(select(Recipe).where(Recipe.is_cocktail == is_cocktail))).all())
        await session.execute(update(Recipe).where(Recipe.id == cocktail.id).values(is_showed=True))
        await session.commit()
        print(cocktail, "dsaadsdasd")
        return cocktail
    except AttributeError:
        return None


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Recipe).where(Recipe.id == product_id).values(data)
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, recipe_id: int):
    query = delete(Recipe).where(Recipe.id == recipe_id)
    await session.execute(query)
    await session.commit()
    return True
