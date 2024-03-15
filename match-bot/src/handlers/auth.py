from aiogram import Router, F, types
from aiogram.filters import or_f, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from redis.asyncio.client import Redis

from utils import login, link

user_private_router = Router()


class Auth(StatesGroup):
    email = State()
    password = State()


@user_private_router.callback_query(or_f(
    F.data.startswith("auth")
))
async def auth(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите email аккаунта с сайта:")
    await state.set_state(Auth.email)
    await callback_query.answer()


@user_private_router.message(StateFilter('*'), Command("отмена"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены")


@user_private_router.message(Auth.email)
async def fix_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await state.set_state(Auth.password)
    await message.answer("Введите пароль к этому аккаунту сайта:")


@user_private_router.message(Auth.password)
async def fix_password(message: types.Message, state: FSMContext, redis: Redis):
    user_data = await state.get_data()
    user_data["password"] = message.text
    login_response = await login(user_data["email"], user_data["password"])
    token = login_response.get("access_token")
    if token:
        await redis.sadd(f"auth:{message.from_user.id}", token)
        link_response = await link(tg_id=message.from_user.id, email=user_data["email"])
        await message.answer(
            f"Успех! Теперь вам будут приходить новости нашей площадки и результаты со статистикой матчей. {link_response}"
        )
    else:
        await message.answer("Неверный логин и/или пароль")
    await state.clear()
