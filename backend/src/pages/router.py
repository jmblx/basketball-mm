import fastapi
from fastapi import Request

from matchmaking.router_5x5 import templates

router = fastapi.APIRouter(prefix="/pages", tags=["pages"])


@router.get("/main")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/continue_google_auth")
async def get_google_auth_page(request: Request):
    return templates.TemplateResponse("google_continue_register.html", {"request": request})
