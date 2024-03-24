from uuid import UUID
import os

import fastapi
from fastapi import Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from tensorflow.keras.models import load_model

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from tournaments.models import SoloMatch

router = fastapi.APIRouter(prefix="/report", tags=["report"])


@router.get("/smurf")
async def smurf_report(
    smurf_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    # apellant: User = Depends(current_user)
):
    # smurf = await session.get(User, smurf_id)
    stmt = (
        select(SoloMatch)
        .where(SoloMatch.players.any(id=smurf_id))
        .order_by(desc(SoloMatch.start_date))
        .limit(7)
    )
    result = await session.execute(stmt)
    last_smurf_matches = result.scalars().all()
    matches_scores = [match.scores for match in last_smurf_matches]
    processed_data = []

    for match in matches_scores:
        if match is not None:
            if match["first_player"]["id"] == smurf_id:
                score = match["first_player"]["score"]
                opponent_score = match["second_player"]["score"]
            else:
                score = match["second_player"]["score"]
                opponent_score = match["first_player"]["score"]

            win = 1 if score > opponent_score else 0
            processed_data.append([score, opponent_score, win])
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(BASE_DIR, "my_model.h5")
    model = load_model(model_path)

    def predict_smurf(match_data):
        prediction = model.predict([match_data])
        return prediction[0][0]

    print(processed_data)
    return {"res": float(predict_smurf(processed_data))}
