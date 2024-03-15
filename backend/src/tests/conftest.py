import asyncio
import os.path
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database import get_async_session, Base
from config import (DB_HOST_TEST, DB_NAME_TEST, DB_PASS_TEST, DB_PORT_TEST,
                    DB_USER_TEST
)
from main import app
from auth.models import Role
from tests.testutils import generate_unique_email

# DATABASE
DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

client = TestClient(app)

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def add_admin_role():
    # Фикстура для добавления роли "admin"
    async with async_session_maker() as session:
        role = Role(name="admin", permissions={})
        session.add(role)
        await session.commit()

@pytest.fixture(scope="function")
async def authenticated_token(ac: AsyncClient, add_admin_role):
    email = generate_unique_email()
    reg_response = await ac.post("/auth/register", json={
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "nickname": email,
        "role_id": 1,
        "pathfile": "string",
        "phone_number": "+79185717510"
    })
    assert reg_response.status_code == 201
    login_response = await ac.post("/auth/jwt/login", data={
        "grant_type": None,
        "username": email,
        "password": "string",
        "scope": "",
        "client_id": None,
        "client_secret": None
    })
    assert login_response.status_code == 200
    print(login_response.json().get("access_token"))
    return login_response.json().get("access_token")


@pytest.fixture(scope="function")
async def authenticated_data(ac: AsyncClient, add_admin_role):
    email = generate_unique_email()
    reg_response = await ac.post("/auth/register", json={
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "nickname": email,
        "role_id": 1,
        "pathfile": "string",
        "phone_number": "+79185717510"
    })
    assert reg_response.status_code == 201
    login_response = await ac.post("/auth/jwt/login", data={
        "grant_type": None,
        "username": email,
        "password": "string",
        "scope": "",
        "client_id": None,
        "client_secret": None
    })
    assert login_response.status_code == 200
    access_token = login_response.json().get('access_token')
    user_data_response = await ac.get("/profile/", headers={"Authorization": f"Bearer {access_token}"})
    yield {"access_token": access_token, "user_data": user_data_response.json()}
    resp_del = await ac.delete(f"/profile/delete/{user_data_response.json().get('id')}")


@pytest.fixture(scope="function")
async def team_mock(ac: AsyncClient, authenticated_token):
    response_add_team = await ac.post("/team/add-new-team", json={
        "name": "test team",
        "pathfile": "string"
    }, headers={"Authorization": f"Bearer {authenticated_token}"})
    print(response_add_team.text, response_add_team.status_code)
    yield response_add_team.json().get("team_id")
    print("s")


@pytest.fixture(scope="function")
async def driver1(authenticated_token):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("http://localhost:8000/finding-match/1x1/")
    # Установка токена в localStorage
    script = f"localStorage.setItem('auth_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MmViMGEwOC00YmE5LTQwNmUtOWYzMi1jOTlkZWExOTUwNTAiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTcwOTc3NzA5OH0.AQI9laFI9EOC8KEsB9iWMTgIEdwyZL7UQBW09Z1QNV0');"
    driver.execute_script(script)
    driver.refresh()  # Обновите страницу, чтобы учесть новый токен
    yield driver
    driver.quit()

# Фикстура для второго драйвера
@pytest.fixture(scope="function")
async def driver2(authenticated_token):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("http://localhost:8000/finding-match/1x1/")
    # Установка токена в localStorage
    script = f"localStorage.setItem('auth_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0ZWJlYzgwNC00MGI0LTQ4MGMtYWUwMC05MGNhMjQzZDAyM2UiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTcwOTc4MjU1NH0.2uITkHnltFfbw5nE4OROStOddK8nm7hsbxJ6EhUeg3c');"
    driver.execute_script(script)
    driver.refresh()  # Обновите страницу, чтобы учесть новый токен
    yield driver
    driver.quit()

