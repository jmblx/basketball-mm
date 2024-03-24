import smtplib
import uuid
from email.message import EmailMessage
from typing import Optional
import secrets

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
    exceptions,
    models,
    schemas,
)
from sqlalchemy import func

from auth.utils import get_user_db
from config import SECRET_AUTH, SMTP_HOST, SMTP_PORT
from auth.models import User

from config import SMTP_PASSWORD, SMTP_USER
from database import async_session_maker


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        pass

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):  ## Отправка пользователю на почту токена для обновления пароля
        email = EmailMessage()
        email["Subject"] = "Восстановление пароля"
        email["From"] = SMTP_USER
        email["To"] = user.email
        email_content = f"""
            Здравствуйте! На вашем аккаунте пытались сбросить пароль
            Если это не вы то игнорируйте сообщение. Иначе можете сбросить пароль
            по следующей ссылке: {token}
        """
        email.set_content(email_content, subtype="html")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(email)

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        #        async with async_session_maker() as session:
        token = secrets.token_urlsafe(32)
        user_dict["email_confirmation_token"] = token
        #            await session.add(user)
        email = EmailMessage()
        email["Subject"] = "Подтвердите регистрацию"
        email["From"] = SMTP_USER
        email["To"] = user_dict.get("email")
        email_content = f"""
                   Здравствуйте! Если вы зарегестрировались на сайте basketball-mm,
                   используя эту почту, то перейдите по следующей ссылке: localhost:8000/custom/email-confirmation/{token}
               """
        email.set_content(email_content, subtype="html")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(email)
        user_dict["role_id"] = 1
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["search_vector"] = func.to_tsvector(
            "russian", user_dict["nickname"]
        )
        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
