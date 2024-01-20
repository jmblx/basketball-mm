from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy import text
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware

# import sentry_sdk

from auth.base_config import (
    auth_backend,
    fastapi_users, google_oauth_client,
)
from auth.schemas import UserCreate, UserRead, UserUpdate
# from config import SENTRY_URL, SECRET_AUTH
from auth.custom_auth_router import router as custom_auth_router
from config import REDIS_HOST, REDIS_PORT, SECRET_AUTH
from database import async_session_maker
from matchmaking.router import router as matchmaking_router
from matchmaking.router_5x5 import router as matchmaking_5x5_router
from matchmaking.router_5x5_add import router as matchmaking_5x5_router_add
from report.router import router as report_router
from social.router import router as social_router
from solomatch.router import router as solomatch_router
from stats.router import router as stats_router
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
app.include_router(matchmaking_5x5_router)
app.include_router(matchmaking_5x5_router_add)
app.include_router(solomatch_router)
app.include_router(stats_router)
app.include_router(report_router)
app.include_router(social_router)


app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        SECRET_AUTH,
        # redirect_url="http://127.0.0.1:8000/",
        is_verified_by_default=True,
    ),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_associate_router(
        google_oauth_client, UserRead, "SECRET"
    ),
    prefix="/auth/associate/google",
    tags=["auth"],
)


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
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
