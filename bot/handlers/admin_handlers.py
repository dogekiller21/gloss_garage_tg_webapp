from aiogram import types
from aiogram.types import WebAppInfo
from aiogram.utils.exceptions import BadRequest

from bot.main import dp, bot


@dp.message_handler(commands=["link"])
async def change_link_command(message: types.Message):
    args = message.get_args()
    if not args:
        await message.answer("Киньте ссылочку")
        return
    webapp_info = WebAppInfo(url=args)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="Приложение", web_app=webapp_info)
    )
    try:
        await message.answer("Кнопочка для приложения", reply_markup=keyboard)
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=types.MenuButtonWebApp(text="Приложение", web_app=webapp_info),
        )
    except BadRequest:
        await message.answer("Ссылка некорретная")
        return
