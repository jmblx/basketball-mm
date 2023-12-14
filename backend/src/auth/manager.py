import smtplib
import uuid
from email.message import EmailMessage
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
    exceptions,
    models,
    schemas,
)

from auth.utils import get_user_db
from config import SECRET_AUTH, SMTP_HOST, SMTP_PORT
from auth.models import User

from config import SMTP_PASSWORD, SMTP_USER


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ): ## Отправка пользователю на почту токена для обновления пароля
        email = EmailMessage()
        email['Subject'] = 'Восстановление пароля'
        email['From'] = SMTP_USER
        email['To'] = user.email
        email_content = f"""
            Здравствуйте! На вашем аккаунте пытались сбросить пароль
            Если это не вы то игнорируйте сообщение. Иначе можете сбросить пароль
            по следующей ссылке: {token}
        """
        email.set_content(
            email_content,
            subtype='html'
        )
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
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
