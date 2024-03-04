from httpx import AsyncClient

from tests.conftest import async_session_maker
from sqlalchemy import insert, select

from tests.conftest import async_session_maker
from auth.models import Role


async def test_role(self, ac: AsyncClient, authenticated_token):
    response = await ac.post("/profile/add-role", json={
        "name": "user",
        "permissions": {}
    }, headers={"Authorization": f"Bearer {authenticated_token}"})
    assert response.status_code == 200

    async with async_session_maker() as session:
        stmt = select(Role).order_by(Role.id)
        result = (await session.execute(stmt)).scalars().all()
    res = result[-1].__dict__
    res.pop('_sa_instance_state')

    assert res == {'id': 3, 'name': 'user', 'permissions': {}}, "Роль не добавилась"
