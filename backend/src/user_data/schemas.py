from pydantic import BaseModel, EmailStr


class LinkTG(BaseModel):
    user_email: EmailStr
    tg_id: int
