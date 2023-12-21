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
from sqlalchemy import select, and_
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

    async def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            async with async_session_maker() as session:
                player = await session.get(User, user_id)
                player.searching = False
                await session.add(player)
                await session.commit()

    async def find_match(self, player_id: UUID):
        async with async_session_maker() as session:
            player = await session.get(User, player_id)
            while player and player.searching:
                result = await session.execute(
                    select(User).where(
                        and_(User.searching == True, User.id != player.id)
                    )
                )
                for other_player in result.scalars():
                    if abs(other_player.solo_rating - player.solo_rating) <= 100:
                        match = SoloMatch(players=[player, other_player])
                        session.add(match)
                        await session.commit()
                        player.searching = False
                        other_player.searching = False
                        session.add_all([player, other_player])
                        await session.commit()
                        await manager.disconnect(player.id)
                        await manager.disconnect(other_player.id)
                        return
                await asyncio.sleep(3)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.get("/")
def get_chat_page(request: Request):
    return templates.TemplateResponse("matchmaking.html", {"request": request})


@router.websocket("/ws/{player_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        player_id,
):
    async with async_session_maker() as session:
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
            await manager.find_match(player_id)
        except WebSocketDisconnect:
            await manager.disconnect(player.id)
