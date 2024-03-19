import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DB_PASS, DB_HOST, DB_PORT, DB_NAME, DB_USER
from database.models import Base

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# async def create_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#
# async def drop_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
