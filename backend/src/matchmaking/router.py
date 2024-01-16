import asyncio
from datetime import datetime
import json
from typing import Annotated
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

router = fastapi.APIRouter(prefix="/finding-match", tags=["matchmaking"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.ready_players: dict[UUID, bool] = {}
        self.match_candidates: dict[UUID, UUID] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        print("1")
        await websocket.accept()
        print("2")
        self.active_connections[user_id] = websocket
        self.ready_players[user_id] = False

    async def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            del self.ready_players[user_id]
            if user_id in self.match_candidates:
                del self.match_candidates[user_id]
            async with async_session_maker() as session:
                player = await session.get(User, user_id)
                player.searching = False
                session.add(player)
                await session.commit()

    async def set_player_ready(self, player_id: UUID):
        self.ready_players[player_id] = True
        opponent_id = self.match_candidates.get(player_id)
        if opponent_id and self.ready_players.get(opponent_id, False):
            await self.start_match(player_id, opponent_id)

    async def start_match(self, player_id: UUID, opponent_id: UUID):
        async with async_session_maker() as session:
            player = await session.get(User, player_id)
            opponent = await session.get(User, opponent_id)
            player.solomatch_played += 1
            opponent.solomatch_played += 1
            match = SoloMatch(players=[player, opponent], start_date=datetime.utcnow())
            session.add_all([match, player, opponent])

            await session.commit()
            await self.active_connections[player_id].send_text(
                json.dumps({"action": "matchStarted", "matchId": match.id})
            )
            await self.active_connections[opponent_id].send_text(
                json.dumps({"action": "matchStarted", "matchId": match.id})
            )

    async def find_match(self, player_id: UUID):
        async with async_session_maker() as session:
            player = await session.get(User, player_id)
            while player and player.searching:
                result = await session.execute(
                    select(User).where(
                        and_(User.searching==True, User.id != player.id)
                    )
                )
                for other_player in result.scalars():
                    if abs(other_player.solo_rating - player.solo_rating) <= 100:
                        self.match_candidates[player_id] = other_player.id
                        self.match_candidates[other_player.id] = player_id
                        await self.active_connections[player_id].send_text(
                            json.dumps({"action": "matchFound", "opponentId": str(other_player.id)})
                        )
                        await self.active_connections[other_player.id].send_text(
                            json.dumps({"action": "matchFound", "opponentId": str(player_id)})
                        )
                        return
                await asyncio.sleep(3)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.get("/solo")
def get_chat_page(request: Request):
    return templates.TemplateResponse("matchmaking.html", {"request": request})


@router.websocket("/solo/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: UUID):
    print("sda")
    await manager.connect(websocket, player_id)
    try:
        async with async_session_maker() as session:
            player = await session.get(User, player_id)
            player.searching = True
            session.add(player)
            await session.commit()
            print(player.searching)
        await manager.find_match(player_id)
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            if data_json.get('action') == 'confirmReady':
                await manager.set_player_ready(player_id)

    except WebSocketDisconnect:
        await manager.disconnect(player_id)
