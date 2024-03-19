from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


Base = declarative_base()


class Recipe(Base):
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    ingredients: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    is_cocktail: Mapped[bool]
    photo_id: Mapped[str] = mapped_column(String(1500))
    is_showed: Mapped[bool] = mapped_column(default=False)
