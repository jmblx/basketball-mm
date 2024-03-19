from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)

# async def admin_check(
#     message
# ):
#     return str(message.from_user.id) in ADMIN_LIST


def get_settings_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text="Логин", callback_data=f"auth"),
    )
    return keyboard.adjust(1).as_markup()  # Настройте макет под ваши нужды
