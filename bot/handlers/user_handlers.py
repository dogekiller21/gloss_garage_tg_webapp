from aiogram import types
from bot.main import dp, bot, webapp_info


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):

    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="Приложение", web_app=webapp_info)
    )
    await message.answer(
        f"Добро пожаловать!\n\n"
        f"Личный кабинет доступен по кнопочке снизу или слева от вашей клавиатуры!\n\n"
        f"Наш адрес - xxx\n"
        f"Будем рады видеть вас с 9:00 до 21:00 в каждый день недели!",
        reply_markup=keyboard
    )
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(text="Приложение", web_app=webapp_info),
    )


@dp.message_handler()
async def answer_button_handler(message: types.Message):
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(text="Приложение", web_app=webapp_info),
    )
