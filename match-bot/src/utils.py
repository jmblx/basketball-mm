import os

import aiohttp


async def login(email, password):
    url = f'http://{os.getenv("BACKEND")}:8000/auth/jwt/login'
    data = f"username={email}&password={password}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.json()


async def link(tg_id: int, email: str):
    url = f"http://{os.getenv('BACKEND')}:8000/profile/link/tg/"
    headers = {'Content-Type': 'application/json'}
    data = {'tg_id': tg_id, 'user_email': email}

    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=data, headers=headers) as response:
            if response.status == 404:  # Вы можете адаптировать обработку статусных кодов под свои нужды
                return {'response': 'произошла ошибка'}
            return (await response.json()).get('response')
