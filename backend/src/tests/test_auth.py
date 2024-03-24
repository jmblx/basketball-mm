from httpx import AsyncClient


class TestUserProfile:

    async def test_register(self, ac: AsyncClient, add_admin_role):
        response = await ac.post(
            "/auth/register",
            json={
                "email": "snich@mail.ru",
                "password": "string",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "nickname": "string",
                "role_id": 1,
                "pathfile": "string",
                "phone_number": "+79185717510",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "snich@mail.ru"
        assert response.json()["phone_number"] == "+79185717510"

    async def test_login(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "grant_type": None,
                "username": "snich@mail.ru",
                "password": "string",
                "scope": "",
                "client_id": None,
                "client_secret": None,
            },
        )
        assert response.status_code == 200
        assert response.json()["access_token"]
        assert response.json()["token_type"] == "Bearer"
        assert response.json()["expires_in"] == 3600
