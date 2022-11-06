from aiogram import Bot, Dispatcher, executor
from aiogram import types
from aiogram.types.web_app_info import WebAppInfo

from bot.config import FRONT_END_LINK
from config import TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["test"])
async def test_command(message: types.Message):
    webapp_info = WebAppInfo(url=FRONT_END_LINK)

    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="WebApp", web_app=webapp_info)
    )
    await message.answer(text="test", reply_markup=keyboard)
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(text="Приложение", web_app=webapp_info),
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
