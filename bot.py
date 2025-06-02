import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

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
    ("IMG_7087.jpeg", "У нас с тобой все получится!"),
    ("IMG_7761.jpeg", "С тобой даже самые будничные дни — как праздник."),
    ("2B7E2B03.jpeg", "Ты умеешь быть настоящим. И это бесценно."),
    ("B31FB0E2.jpeg", "Я люблю нас. Особенно — в такие моменты."),
    ("TXD5wkJc.jpeg", "Ты — мой самый лучший человек на свете."),
]

tasks = [
    ("🎯 Первое задание: сфотографируй завтрак и отправь его сюда.", "✅ Завтрак — залог отличного дня! Молодец!"),
    ("📞 Позвони маме и поздравь её с днем рождения тебя 😊", "✅ Супер! Мамы — это святое ❤️"),
    ("🌊 Зайди в море один раз и пришли фото/видео!", "✅ Герой! Сила воды — с тобой!"),
    ("🍴 Выбери ресторан на вечер (пришли 3 варианта)", "✅ Шеф, вы сделали вкусный выбор 😋"),
    ("🧥 Оденься красиво для вечера. Жду селфи!", "✅ Красавчик! Ты сразишь всех 😍"),
    ("💬 Пока ждёшь жену, пройди тест — будет весело!", "✅ Ну ты знаток! Респект 👏"),
    ("🍷 Выпей аперитив и сфоткай бокал", "✅ Пусть вечер будет таким же ярким, как ты!"),
    ("🥂 Ужин с женой — сделай фото на память", "✅ Вы идеальная пара!"),
    ("🍾 Возьми просекко/вино и вернись в номер", "✅ Осталось чуть-чуть до подарка..."),
    ("🎁 Найди подарок: он под 'штукой, которая у нас была всякая разная, даже на половину кровати'", "🥳 Нашёл! С днём рождения, любимый 💖"),
]

quiz_questions = [
    ("Какой сериал ты никогда не хочешь смотреть?", ["Игра престолов", "Клюквенный щербет", "Во все тяжкие"]),
    ("Кто поёт твою любимую песню?", ["Rihanna", "Zivert", "Dua Lipa"]),
    ("Что я чаще всего говорю по утрам?", ["Доброе утро, котик", "Где мои тапки?", "Сварил кофе?"]),
]

user_states = {}

@dp.message_handler(commands=["start", "go"])
async def send_welcome(message: types.Message):
    if message.from_user.id in USER_IDS:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Начать игру", callback_data="start_game")
        )
        user_states[message.from_user.id] = {"task": 0, "in_quiz": False}
        await message.answer("🎉 Привет! Готов начать день с сюрпризами?", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "start_game")
async def start_game(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    await send_task(user_id)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {})
    task_idx = state.get("task", 0)

    if task_idx < len(tasks):
        await message.reply(tasks[task_idx][1])  # похвала
        user_states[user_id]["task"] += 1
        await send_task(user_id)
    else:
        await message.reply("🎉 Ты выполнил все задания! Проверь, не ждёт ли тебя где-то подарок 😉")

@dp.message_handler()
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {})

    if state.get("in_quiz"):
        current_q = state.get("quiz_q", 0)
        if current_q < len(quiz_questions) - 1:
            user_states[user_id]["quiz_q"] += 1
            await send_quiz_question(user_id)
        else:
            state["in_quiz"] = False
            await bot.send_message(user_id, "🧠 Поздравляю, ты почти у цели! Готов к последнему заданию?")
            await send_task(user_id)

async def send_task(user_id):
    state = user_states[user_id]
    task_idx = state.get("task", 0)

    if task_idx == 5:
        state["in_quiz"] = True
        state["quiz_q"] = 0
        await send_quiz_question(user_id)
        return

    if task_idx < len(tasks):
        text = tasks[task_idx][0]
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Готово ✅", callback_data="done"))
        await bot.send_message(user_id, text, reply_markup=markup)
    else:
        await bot.send_message(user_id, "🎉 Все задания выполнены. Ты молодец! Осталось только найти подарок 😉")

@dp.callback_query_handler(lambda c: c.data == "done")
async def handle_done(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.reply("👌 Жду фото/подтверждение!")

async def send_quiz_question(user_id):
    state = user_states[user_id]
    q_idx = state["quiz_q"]
    q, options = quiz_questions[q_idx]
    markup = InlineKeyboardMarkup()
    for opt in options:
        markup.add(InlineKeyboardButton(opt, callback_data="quiz_ans"))
    await bot.send_message(user_id, f"🧠 Вопрос: {q}", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "quiz_ans")
async def handle_quiz_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.reply("✅ Ответ записан!")
    await handle_text(callback_query.message)

async def scheduled_messages():
    for user_id in USER_IDS:
        await bot.send_message(user_id, "🌅 Доброе утро! Сегодня ты в игре. С тебя — настроение и задания, с меня — сюрприз ❤️")
        for i, (photo, caption) in enumerate(photos_with_captions):
            await asyncio.sleep(3600 if i > 0 else 10)
            with open(f"media/{photo}", "rb") as img:
                await bot.send_photo(user_id, img, caption=caption)

async def on_startup(dp):
    asyncio.create_task(scheduled_messages())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
