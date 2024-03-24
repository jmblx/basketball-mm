import datetime
import random
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker
from tournaments.models import (
    Tournament,
    Match,
    TeamTournament,
    TeamMatch,
    StatusEvent,
)


async def fill_tournament(tournament_id: int, session: AsyncSession):
    tournament = await session.get(Tournament, tournament_id)
    start_tournament_day = tournament.start_date
    matches = []
    day_offset = 0

    def create_datetime(hour, minute, day_offset=0):
        while minute >= 60:
            minute -= 60
            hour += 1
        while hour >= 24:
            hour -= 24
            day_offset += 1
        return start_tournament_day.replace(
            hour=hour, minute=minute
        ) + datetime.timedelta(days=day_offset)

    for stage in range(1, tournament.number_stages + 1):
        for match in range(int(tournament.number_participants / stage / 2)):
            cur_match_start_date = create_datetime(
                start_tournament_day.hour,
                start_tournament_day.minute,
                day_offset=day_offset,
            )
            end_date = create_datetime(
                start_tournament_day.hour, start_tournament_day.minute + 30
            )
            match_data = {
                "status": "opened",
                "stage": stage,
                "number_in_stage": match,
                "tournament_id": tournament.id,
                "start_date": cur_match_start_date,
                "end_date": end_date,
            }
            matches.append(match_data)
            if end_date != create_datetime(18, 0):
                start_tournament_day = end_date
            else:
                day_offset += 1
                start_tournament_day = create_datetime(9, 0)

    stmt_insert_match = insert(Match).values(matches)
    await session.execute(stmt_insert_match)
    await session.commit()


async def fill_tournament_teams(
    tournament_id: int,
):
    async with async_session_maker() as session:
        tournament = await session.get(Tournament, tournament_id)
        all_teams = await get_data(
            TeamTournament.team_fk,
            TeamTournament.tournament_fk == tournament_id,
            is_scalar=False,
        )
        all_matches = await get_data(
            Match.id,
            Match.tournament_id == tournament_id,
            is_scalar=False,
        )
        random.shuffle(all_teams)
        arr_team_match_data = []
        team_counter = 0
        match_counter = 0
        for stage in range(1, tournament.number_stages + 1):
            for match in range(int(tournament.number_participants / stage)):
                if stage == 1:
                    team_match_data = {
                        "match_fk": all_matches[match_counter // 2],
                        "team_fk": all_teams[team_counter],
                    }
                    team_counter += 1
                    match_counter += 1
                else:
                    team_match_data = {
                        "match_fk": all_matches[match_counter // 2],
                        "team_fk": None,
                    }
                    match_counter += 1
                arr_team_match_data.append(team_match_data)

        stmt_insert_team_match = insert(TeamMatch).values(arr_team_match_data)
        await session.execute(stmt_insert_team_match)
        tournament.status = StatusEvent.actived
        await session.commit()


async def get_data(
    class_,
    filter,
    is_scalar: bool = False,
):
    async with async_session_maker() as session:
        stmt = select(class_).where(filter)
        if is_scalar:
            res_query = await session.execute(stmt)
            res = res_query.scalar()
        else:
            res_query = await session.execute(stmt)
            res = res_query.fetchall()
            res = [result[0] for result in res]
    return res


async def get_tournaments(status: StatusEvent):
    async with async_session_maker() as session:
        query = select(Tournament).where(Tournament.status == status)
        res = (await session.execute(query)).all()
        result = {"status": "success", "data": dict(), "details": None}
        for tournament in range(len(res)):
            tournament_obj = res[tournament][0].__dict__
            tournament_obj.pop("_sa_instance_state")
            result["data"][f"tournament_{tournament}"] = tournament_obj

        return result


def get_match_result_data(player_match_result: dict) -> tuple:
    return (player_match_result.get("id"), player_match_result.get("score"))


def form_player_json(player_id: UUID, score: int):
    return {
        "id": player_id,
        "score": score,
    }
