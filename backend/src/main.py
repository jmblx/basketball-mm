from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware

# import sentry_sdk

from auth.base_config import (
    auth_backend,
    fastapi_users,
)
from auth.schemas import UserCreate, UserRead, UserUpdate
# from config import SENTRY_URL, SECRET_AUTH
from auth.custom_auth_router import router as custom_auth_router
from matchmaking.router import router as matchmaking_router
from teams.router import router as teams_router
from tournaments.router import router as tournaments_router
from user_data.router import router as user_data_router

# sentry_sdk.init(
#     dsn=SENTRY_URL,
#     traces_sample_rate=1.0,
#     profiles_sample_rate=1.0,
# )

app = FastAPI(title="requests proceed API")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Кастомные

app.include_router(custom_auth_router)
app.include_router(teams_router)
app.include_router(tournaments_router)
app.include_router(user_data_router)
app.include_router(matchmaking_router)

# Регулировка обращений к API с других адресов
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
