import asyncio
import time

from httpx import AsyncClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_200_OK

from auth.models import Team
from tests.conftest import authenticated_data, async_session_maker


class TestTeam:

    async def test_create_team(self, ac: AsyncClient, authenticated_data: dict):
        response = await ac.post("/team/add-new-team", json={
            "name": "ТЕСТОвая тим казлоф и уродов",
            "pathfile": "string"
        }, headers={"Authorization": f"Bearer {authenticated_data.get('access_token')}"})
        assert response.status_code == 200
        async with async_session_maker() as session:
            stmt = select(Team).where(Team.id == 1)
            res = (await session.execute(stmt)).scalar()
        assert str(res.captain_id) == authenticated_data.get("user_data").get("id")
        assert res.name == "ТЕСТОвая тим казлоф и уродов"
        assert res.slug == slugify("ТЕСТОвая тим казлоф и уродов", lowercase=True)

    async def test_join_team(self, ac: AsyncClient, authenticated_data: dict, team_mock):

        async with async_session_maker() as session:
            print("Есть команда:", (await session.execute(select(Team))).scalar_one().id)
        response = await ac.post(
            "/team/join-team",
            headers={"Authorization": f"Bearer {authenticated_data.get('access_token')}"},
            params={"team_id": team_mock}
        )
        response.status_code = HTTP_200_OK
        async with async_session_maker() as session:
            stmt = (
                select(Team).where(Team.id == team_mock).options(selectinload(Team.players))
            )
            team = (await session.execute(stmt)).scalar()
            assert authenticated_data.get("user_data").get("id") in [str(p.id) for p in team.players]

    async def test_matchmaking(self, driver1, driver2):
        await asyncio.sleep(2)
        start_button1 = driver1.find_element(By.ID, "startMatchmaking")
        start_button1.click()
        await asyncio.sleep(1)
        start_button2 = driver2.find_element(By.ID, "startMatchmaking")
        start_button2.click()
        await asyncio.sleep(2)
        confirm_button1 = WebDriverWait(driver1, 30).until(
            EC.visibility_of_element_located((By.ID, "confirmReady"))
        )
        confirm_button1.click()
        await asyncio.sleep(2)
        confirm_button2 = WebDriverWait(driver2, 30).until(
            EC.visibility_of_element_located((By.ID, "confirmReady"))
        )
        confirm_button2.click()
