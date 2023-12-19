from datetime import datetime
from typing import Annotated
import asyncio
from uuid import UUID

import fastapi
from fastapi import (
    WebSocket, WebSocketDisconnect, Query,
    WebSocketException, Depends, Request
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import async_session_maker
from tournaments.models import Match, SoloMatch

templates = Jinja2Templates(directory="templates")

router = fastapi.APIRouter(prefix="/matchmaking", tags=["matchmaking"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def find_match(self, player_id: UUID, session: AsyncSession):
        player = await session.get(User, player_id)
        while player and player.searching:
            async for other_player in await (session.execute(
                session.query(User).filter(User.searching == True, User.id != player.id)
            )).scalars():
                if abs(other_player.solo_rating - player.solo_rating) <= 100:
                    match = SoloMatch(players=[player, other_player], status=SoloMatch.status.pending)
                    session.add(match)
                    await session.commit()
                    await self.active_connections[player.id].send_text(f"Match found with player {other_player.id}")
                    await self.active_connections[other_player.id].send_text(f"Match found with player {player.id}")
                    player.searching = False
                    other_player.searching = False
                    session.add_all([player, other_player])
                    await session.commit()
                    return
            await asyncio.sleep(3)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.get("/")
def get_chat_page(request: Request):
    logger.debug("Your debug message")
    return templates.TemplateResponse("matchmaking.html", {"request": request})

import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

@router.websocket("/ws/{player_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        player_id,
):
    async with async_session_maker() as session:
        logger.debug("Your debug message")
        await manager.connect(websocket, player_id)
        player = await session.get(User, player_id)
        player.searching = True
        await session.commit()
        print(player.searching)
        if not player:
            print(f"Player not found: {player_id}")
            await websocket.close(code=1000)
            return
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {data}", websocket)
        except WebSocketDisconnect:
            player.searching = False
            await session.commit()
            manager.disconnect(player.id)
