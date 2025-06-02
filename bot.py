import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os
from datetime import datetime, timedelta

API_TOKEN = os.getenv("API_TOKEN")
USER_IDS = [int(uid) for uid in os.getenv("USER_IDS", "").split(",")]

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

photos_with_captions = [
    ("IMG_9126.jpeg", "☀️ Когда ты держишь мою руку — мне спокойно."),
    ("IMG_9111.jpeg", "Ты — мой дом."),
    ("IMG_4979.jpeg", "Ты- самый лучший. Помни об этом всегда!"),
    ("IMG_5377.jpeg", "Ты самый умный мужчина из всех, кого я знаю."),
    ("IMG_5390.jpeg", "Ты - моя опора."),
    ("IMG_5863.jpeg", "Люблю, когда ты смотришь так, как на этом фото."),
    ("IMG_6353.jpeg", "Ты умеешь быть разным — и я люблю каждое твое состояние."),
    ("IMG_7087.jpeg", "У нас с тобой все получится!."),
    ("IMG_7761.jpeg", "С тобой даже самые будничные дни — как праздник."),
    ("2B7E2B03.jpeg", "Ты умеешь быть настоящим. И это бесценно."),
    ("B31FB0E2.jpeg", "Я люблю нас. Особенно — в такие моменты."),
    ("TXD5wkJc.jpeg", "Ты — мой самый лучший человек на свете"),
]

async def scheduled_messages():
    for user_id in USER_IDS:
        await bot.send_message(user_id, "🌅 Доброе утро! Сегодня ты в игре. С тебя - хорошее настроение и выполнение заданий, а с меня- сюрприз! ❤️")
        for i, (photo, caption) in enumerate(photos_with_captions):
            await asyncio.sleep(3600 if i > 0 else 10)
            with open(f"media/{photo}", "rb") as img:
                await bot.send_photo(user_id, img, caption=caption)

@dp.message_handler(commands=["start", "go"])
async def send_welcome(message: types.Message):
    if message.from_user.id in USER_IDS:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Начать игру", callback_data="start_game")
        )
        await message.answer("🎉 Привет! Готов начать день с сюрпризами?", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "start_game")
async def start_game(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "🎯 Первое задание: сфотографируй завтрак и отправь его сюда.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await message.reply("✅ Фото получено! Жди следующее задание.")

async def on_startup(dp):
    asyncio.create_task(scheduled_messages())

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
