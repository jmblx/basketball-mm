import fastapi
from fastapi import Depends, Response, UploadFile, Request
from fastapi_users.password import PasswordHelper, PasswordHelperProtocol
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from auth.schemas import UserGoogleRegistration
from database import get_async_session
from matchmaking.router import templates

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


@router.get("/auth-page")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@router.post("/final_auth_google")
async def set_final_auth_google(
    data: UserGoogleRegistration,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    data = {key: value for key, value in data.model_dump().items() if value is not None}
    pwd = PasswordHelper()
    data["hashed_password"] = pwd.hash(data.get("password"))
    data.pop("password")
    await session.execute(update(User).where(User.id == user.id).values(data))
    await session.merge(user)
    await session.commit()
    return {
        "nickname": user.nickname,
        "password": pwd.hash("string")

    }
