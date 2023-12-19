import datetime
from typing import Optional

from pydantic import BaseModel

from tournaments.models import StatusEvent


class TournamentSchema(BaseModel):
    status: StatusEvent
    placemark: str
    number_participants: int
    start_date: datetime.datetime = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    pathfile: Optional[str] = None
