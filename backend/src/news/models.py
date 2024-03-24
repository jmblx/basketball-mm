from typing import List

from sqlalchemy import TEXT, ForeignKey, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from auth import models as auth_models
from database import Base
from my_type_notation import intpk


class News(Base):
    __tablename__ = "news"

    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(nullable=False, type_=VARCHAR(30))
    text: Mapped[str] = mapped_column(type_=VARCHAR(length=2000))
    pathfile: Mapped[str] = mapped_column(nullable=True)
    slug: Mapped[str] = mapped_column(
        unique=True, type_=VARCHAR(30), nullable=True
    )
    category: Mapped["NewsCategory"] = relationship(
        back_populates="news", uselist=False
    )
    cat_id: Mapped[int] = mapped_column(ForeignKey("news_category.id"))
    # author: Mapped["auth_models.User"] = relationship(back_populates="news", uselist=False)
    # author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))


class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=True)
    news: Mapped[List["News"]] = relationship(
        back_populates="category", uselist=True
    )
