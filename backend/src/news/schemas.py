from typing import Optional

from pydantic import BaseModel


class AddNews(BaseModel):
    title: str
    text: str
    pathfile: str
    cat_id: int


class UpdateNews(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    cat_id: Optional[int] = None


class AddCategory(BaseModel):
    name: str


class UpdateCategory(BaseModel):
    name: str
