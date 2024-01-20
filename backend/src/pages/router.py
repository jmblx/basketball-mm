import fastapi
from fastapi import Request

from matchmaking.router_5x5 import templates

router = fastapi.APIRouter(prefix="/pages", tags=["pages"])


@router.get("/main")
def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
