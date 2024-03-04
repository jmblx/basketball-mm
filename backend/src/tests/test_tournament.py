from httpx import AsyncClient


async def test_register(self, ac: AsyncClient):
    response = await ac.post("/add/tournament", json={
      "status": "OPENED",
      "placemark": "string",
      "number_participants": 4,
      "start_date": "2023-11-13 11:06:16",
      "pathfile": "string"
    })

    assert response.status_code == 201
