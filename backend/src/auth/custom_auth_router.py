import fastapi
from fastapi import Depends, Response, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session

router = fastapi.APIRouter(prefix="/custom", tags=["custom-auth"])

@router.get("/email-confirmation/{token}")
async def processing_request(
    token: str,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    # user: User = Depends(current_user),
):
    try:
        await session.execute(
            update(User).where(User.email_confirmation_token == token)
            .values(
                {
                    "is_email_confirmed": True,
                    "email_confirmation_token": None
                }
            )
        )
        await session.commit()
    except Exception as e:
        print(e)
        response.status_code = HTTP_400_BAD_REQUEST
        return {
            "details": "invalid url for email confirmation"
        }

