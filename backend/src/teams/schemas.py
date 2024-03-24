from typing import Optional, List

from pydantic import BaseModel


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    is_captain_only_search: Optional[bool] = None


# class CheckCaptainship(BaseModel):
#     user_id: int,
#     team_id


class GetTeamImages(BaseModel):
    team_ids: List
