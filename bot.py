
# -*- coding: utf-8 -*-
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from datetime import datetime, timedelta

API_TOKEN = os.getenv("API_TOKEN")
USER_IDS = [int(uid) for uid in os.getenv("USER_IDS", "").split(",")]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === Фото-комплименты ===
photos_with_captions = [
    ("2025-06-02 22.32.51.jpg", "☀️ Когда ты держишь мою руку — мне спокойно."),
    ("2025-06-02 22.33.06.jpg", "Ты — мой дом."),
    ("2025-06-02 22.33.13.jpg", "Ты- самый лучший. Помни об этом всегда!"),
    ("2025-06-02 22.33.19.jpg", "Ты самый умный мужчина из всех, кого я знаю."),
    ("2025-06-02 22.33.25.jpg", "Ты - моя опора."),
    ("2025-06-02 22.33.31.jpg", "Люблю, когда ты смотришь так, как на этом фото."),
    ("2B7E2B03-87C5-4EB1-B46F-093EA26054E1.jpeg", "Ты умеешь быть разным — и я люблю каждое твое состояние."),
    ("B31FB0E2-40C1-4970-9B80-807699C9ADEA.jpeg", "У нас с тобой все получится!"),
]

QUESTS = [
    {"text": "Задание 1: Позавтракать вкусно. Сфоткай свой завтрак — я проверю 😊"},
    {"text": "Теперь позвони своей маме и поздравь ее с тем, что у нее такой прекрасный сын! 😊"},
    {"text": "Теперь задуть свечу  и загадать желание 🎂"},
    {"text": "Фото из моря или бассейна 🌊 Лицо — безумно счастливое!"},
    {"text": "Время аперетива и обеда: выбери пиво/негрони/апероль/чай или воду и пришли мне фото бокала или селфи!"},
    {"text": "Выбери ресторан на вечер, где мы отпразднуем твоё 35-летие:\n1. Восточный квартал\n2. Плакучая Ива\n3. САНРЕМО\n4. Читта Маргарита\n5. Реззо"}
]

user_states = {}
current_questions = {}
correct_answers = {
    1: "Путешествуем",
    2: "Игра престолов",
    3: "Не трогай меня",
    4: "В зале в углу",
    5: "Всё зависит от случая",
    6: "Турецкие сериалы",
    7: "За всё это вместе",
    8: "Все вместе",
    9: "Все вместе",
}

questions = {
    1: "Что мы делаем по твоему мнению слишком часто, а я всегда не против?",
    2: "Какой сериал ты не хотел смотреть, я тебя заставила, а потом ты каааак втянулся!",
    3: "Что ты чаще всего говоришь утром?",
    4: "Где чаще всего оказываются твои носки?",
    5: "Кто просыпается раньше?",
    6: "Что любит твоя жена, а ты не очень?",
    7: "За что твоя жена тебя больше всего любит?",
    8: "Твоя суперспособность — это:",
    9: "Чем ты гордишься в себе больше всего?",
    10: "Куда мы точно никогда не поедем в отпуск?",
}

@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    if message.from_user.id in USER_IDS:
        user_states[message.from_user.id] = 0
        await message.answer("🎉 Поздравляю, ты в игре! Сегодня тебя ждёт несколько заданий, а в конце — подарочек.")
        await send_next_quest(message.from_user.id)

async def send_question(user_id, q_num):
    current_questions[user_id] = q_num
    q_text = questions[q_num]
    if q_num == 10:
        await bot.send_message(
            user_id,
            f"🧩 Вопрос 10:\n{q_text} (Открытый ответ)"
        )
    else:
        options = [correct_answers[q_num], "Неверный 1", "Неверный 2"]
        markup = InlineKeyboardMarkup()
        for ans in set(options):
            markup.add(InlineKeyboardButton(ans, callback_data=f"answer_{ans}"))

        await bot.send_message(
            user_id,
            f"🧩 Вопрос {q_num}:\n{q_text}",
            reply_markup=markup
        )

@dp.callback_query_handler(lambda c: c.data == "quest_done")
async def handle_quest_done(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_states[user_id] += 1
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, "✅ Задание выполнено, ты молодец!")
    await send_next_quest(user_id)

@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def handle_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    answer = callback_query.data[len("answer_"):]
    q_num = current_questions.get(user_id, 1)
    correct = correct_answers.get(q_num, "")
    if answer == correct:
        await bot.answer_callback_query(callback_query.id, text="✅ Правильно!")
        if q_num == 10:
            await bot.send_message(user_id, "🎉 Поздравляю, ты прошёл опрос! Ты почти у цели… Скоро тебя ждёт кое-что очень приятное 🎁❤️")
            await bot.send_message(user_id, "🕘 Финальное задание:\nОбними жену и получи подарок 🎁\nТы прошёл игру!")
        else:
            await send_question(user_id, q_num + 1)
    else:
        await bot.answer_callback_query(callback_query.id, text="❌ Неверно. Попробуй ещё раз!")

async def send_hourly_compliments():
    while True:
        now = datetime.now()
        if 9 <= now.hour <= 21:
            index = (now.hour - 9) % len(photos_with_captions)
            for user_id in USER_IDS:
                photo, caption = photos_with_captions[index]
                try:
                    await bot.send_photo(chat_id=user_id, photo=InputFile(photo), caption=caption)
                except Exception as e:
                    logging.error(f"Ошибка при отправке фото: {e}")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(send_hourly_compliments())
    executor.start_polling(dp, skip_updates=True)
