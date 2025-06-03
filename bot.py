# -*- coding: utf-8 -*-
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
from datetime import datetime

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
("2B7E2B03-87C5-4EB1-B46F-093EA26054E1.jpeg", "Ты умеешь быть разным — и я люблю каждое твоё состояние."),
("B31FB0E2-40C1-4970-9B80-807699C9ADEA.jpeg", "У нас с тобой все получится!"),
]

QUESTS = [
{"text": "🍳 Задание 1: Позавтракать вкусно. Сфоткай свой завтрак — я проверю 😊"},
{"text": "📞 Задание 2: Теперь позвони своей маме и поздравь её с тем, что у неё такой прекрасный сын! 💐"},
{"text": "🎂 Задание 3: Время задуть свечу на волшебном торте и загадать желание!"},
{"text": "🌊 Задание 4: Сделай фото из моря или бассейна. Лицо — безумно счастливое!"},
{"text": "🍹 Задание 5: Время аперитива и вкусного обеда! С тебя селфи с бокалом пива/негрони/апероля/чего хочешь!"},
{"text": "💃 Задание 6: Включи свою любимую песню и потанцуй. В качестве пруфов — жена должна видеть!"},
{"text": "📋 Задание 7: Ты почти на финише! Держись ещё чуть-чуть 😉"},
{"text": "🎁 Финальное задание: Найди подарок! Он спрятан под штукой, которая у нас была всякая разная, даже на половину кровати 😄"}
]

compliments = [
"🥐 Завтрак выглядит так, что Michelin бы позавидовал! Что ещё нужно для настроения?",
"📞 Отлично, спасибо! Это было важно. Теперь у нас +100 к карме 💕",
"🎂 Это волшебный торт, волшебный день — и желание? Обязательно сбудется!",
"🏖️ На этом пляже ты — Апполон в своей стихии!",
"🍹 Отличный выбор, Чин-чин! Пусть в этом бокале будет вся лёгкость дня!",
"🕺 Ты — звезда танцпола! Даже если он — балкон 😄",
"🧠 Переходим к весёлому опросу!",
"🎁 Ура! Теперь осталось только найти подарок 🎉"
]

questions = [
{
    "text": "1️⃣ Что мы делаем слишком часто, а я всегда не против?",
    "options": {
        "Путешествуем": (True, "✅ Абсолютно! Лишь бы вместе."),
        "Едим": (False, "Ну я, конечно, вкусно готовлю, но не оно!"),
        "Спим": (False, "Спишь хаха 😴"),
        "Сам знаешь что…": (False, "Мимо, но я не против 😏")
    }
},
{
    "text": "2️⃣ Какой сериал я заставила тебя смотреть, ты сопротивлялся, а потом каааак втянулся!",
    "options": {
        "Зимородок": (False, "Ты, конечно, знаешь всех Корханов, но нет 😅"),
        "Оленёнок": (False, "Выбирали вместе!"),
        "Отчаянные домохозяйки": (False, "Не смотрели... пока ещё))"),
        "Игра престолов": (True, "🐉 О да! Мы ещё решили к персонажам не привязываться 😆")
    }
}
]

user_states = {}
quiz_progress = {}

@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    if message.from_user.id in USER_IDS:
        user_id = message.from_user.id
        user_states[user_id] = 0
        quiz_progress[user_id] = 0
        await message.answer("🎉 Поздравляю, ты в игре! Сегодня тебя ждёт несколько заданий, а в конце — подарочек.")
        await send_next_quest(user_id)

async def send_next_quest(user_id):
    index = user_states.get(user_id, 0)

    if index < len(QUESTS):
        quest_text = QUESTS[index]["text"]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Готово ✅", callback_data="ready"))
        await bot.send_message(
            user_id,
            quest_text + "\n\n📸 Сделал задание? Жми «Готово», если всё выполнено!",
            reply_markup=markup
        )
    elif index == len(QUESTS):
        await bot.send_message(user_id, "🎯 Теперь — мини-викторина 😊")
        quiz_progress[user_id] = 0
        await send_quiz_sequence(user_id)
    else:
        await bot.send_message(user_id, "🎉 Всё выполнено! Поздравляю! 🎈")

@dp.callback_query_handler(lambda c: c.data == "ready")
async def handle_ready(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    index = user_states.get(user_id, 0)

    await callback_query.answer("✅ Задание отмечено как выполненное!")

    if index < len(compliments):
        await bot.send_message(user_id, compliments[index])

    user_states[user_id] += 1
    await send_next_quest(user_id)

quiz_progress = {}

@dp.callback_query_handler(lambda c: c.data.startswith("quiz|||"))
async def handle_quiz_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    parts = callback_query.data.split("|||", 2)

    parts = callback_query.data.split("|||", 2)

if len(parts) < 3:
    comment = "🤔 Неизвестный ответ"
    await callback_query.answer()
    await bot.send_message(user_id, f"❌ Нет, не так! {comment}")
    return

    _, q_idx_str, selected = parts
    try:
        q_idx = int(q_idx_str)
    except ValueError:
        await callback_query.answer("🤔 Неизвестный ответ")
        return

    if q_idx >= len(questions):
        await callback_query.answer("🧠 Викторина уже завершена.")
        return

    current_progress = quiz_progress.get(user_id, 0)
    if q_idx != current_progress:
        await callback_query.answer("⏭ Ответ не принят: ты либо уже прошёл этот вопрос, либо ещё не дошёл до него")
        return

    if selected in question["options"]:
        is_correct, comment = question["options"][selected]
        await callback_query.answer()
        await bot.send_message(user_id, comment)

        if is_correct:
            quiz_progress[user_id] = q_idx + 1
            await asyncio.sleep(1)
            if quiz_progress[user_id] < len(questions):
                await send_quiz_sequence(user_id)
            else:
                await bot.send_message(user_id, "🎉 Ты прошёл все вопросы! 🎁")
                user_states[user_id] += 1
                await send_next_quest(user_id)
        else:
            await bot.send_message(user_id, "❌ Нет, не так! Попробуй ещё раз.")

    else:
        await callback_query.answer("🤔 Неизвестный ответ")
        return

    _, q_idx_str, selected = parts
    try:
        q_idx = int(q_idx_str)
    except ValueError:
        await callback_query.answer("🤔 Неизвестный ответ")
        return

    if q_idx >= len(questions):
        await callback_query.answer("🧠 Викторина уже завершена.")
        return

    current_progress = quiz_progress.get(user_id, 0)
    if q_idx != current_progress:
        await callback_query.answer("⏭ Ответ не принят: ты либо уже прошёл этот вопрос, либо ещё не дошёл до него")
        return

    question = questions[q_idx]
    if selected in question["options"]:
        is_correct, comment = question["options"][selected]
        await callback_query.answer()
        await bot.send_message(user_id, comment)
        if is_correct:
            quiz_progress[user_id] = q_idx + 1
            await asyncio.sleep(1)
            if quiz_progress[user_id] < len(questions):
                await send_quiz_sequence(user_id)
            else:
                await bot.send_message(user_id, "🎉 Ты прошёл все вопросы! 🎁")
                user_states[user_id] += 1
                if user_states[user_id] <= len(QUESTS):
                    await send_next_quest(user_id)
    else:
        await callback_query.answer("🤔 Неизвестный ответ")

questions = [
{
    "text": "1️⃣ Что мы делаем слишком часто, а я всегда не против?",
    "options": {
        "Путешествуем": (True, "✅ Абсолютно! Лишь бы вместе."),
        "Едим": (False, "Ну я, конечно, вкусно готовлю, но не оно!"),
        "Спим": (False, "Спишь хаха 😴"),
        "Сам знаешь что…": (False, "Мимо, но я не против 😏")
    }
},
{
        "text": "2️⃣ Какой сериал я заставила тебя смотреть, ты сопротивлялся, а потом каааак втянулся!",
        "options": {
            "Зимородок": (False, "Ты, конечно, знаешь всех Корханов, но нет 😅"),
            "Оленёнок": (False, "Выбирали вместе!"),
            "Отчаянные домохозяйки": (False, "Не смотрели... пока ещё))"),
            "Игра престолов": (True, "🐉 О да! Мы ещё решили к персонажам не привязываться 😆")
    }
},
{
        "text": "3️⃣ Что ты чаще всего говоришь утром?",
        "options": {
            "Доброе утро, любимая": (False, "Это слишком романтично для утра 🤭"),
            "Сколько время?": (False, "Это я обычно спрашиваю 😉"),
            "Не трогай меня": (True, "✅ Утренний ёжик!"),
            "Я уже сделал кофе": (False, "Нет, ты молча его приносишь ☕")
     }
},
{
        "text": "4️⃣ Где чаще всего оказываются твои носки?",
        "options": {
            "В бельевом ящике": (False, "Это было бы слишком идеально 😅"),
            "На сушилке": (False, "Если повезёт, конечно..."),
            "В зале в углу": (True, "✅ Хронический следователь носков знает 😉"),
            "Ты что, я их всегда убираю": (False, "Ну-ну! 😏")
   }
},
{
        "text": "5️⃣ Кто просыпается раньше?",
        "options": {
            "Ты": (False, "Да ну, серьёзно? 😄"),
            "Я": (False, "Вряд ли..."),
            "Оба одновременно": (False, "Это бывает, но редко"),
            "Всё зависит от случая": (True, "✅ Самый реалистичный ответ!")
  }
},
{
        "text": "6️⃣ Что любит твоя жена, а ты не очень?",
        "options": {
            "Пляжный отдых": (False, "Это вы оба любите 🏖️"),
            "Турецкие сериалы": (True, "✅ Дааа, особенно с драмой!"),
            "Завтрак в ресторане": (False, "Ну кому это не нравится? 😅"),
            "Пешие прогулки": (False, "Ты просто жалуешься, но идёшь 😄")
}
},
{
        "text": "7️⃣ За что твоя жена тебя больше всего любит?",
        "options": {
            "За заботу": (False, "Это важно, но не всё!"),
            "За чувство юмора": (False, "Смешной, но..."),
            "За доброту": (False, "Милый, но это не всё ❤️"),
            "За всё это вместе": (True, "✅ Ну конечно, мой любимый!💖")
    }
},
{
        "text": "8️⃣ Твоя суперспособность — это:",
        "options": {
            "Видеть хаос и оставаться спокойным": (False, "Хм... не всегда 😅"),
            "Быть мужчиной мечты": (False, "Почти 😉"),
            "Находить вкусную еду": (False, "Это да, но не только!"),
            "Занимать всю кровать": (False, "Правда... но не суперспособность 😆"),
            "Всё вместе": (True, "✅ Идеальный набор 💪")
}
},
{
        "text": "9️⃣ Чем ты гордишься в себе больше всего?",
        "options": {
            "Умом": (False, "Это важно, но не всё"),
            "Спокойствием": (False, "Не всегда, честно"),
            "Силой": (False, "Ну, ты не Халк же 😅"),
            "А надо всем вместе 💪🧠🧘‍♂️": (True, "✅ Именно! Вот это я понимаю 💯")
}
},
{
        "text": "🔟 Куда мы точно никогда не поедем в отпуск?",
        "options": {
            "Ответь сам 😉": (True, "🧳 Просто знай — я всё помню 😄")
        }
    }
]
quiz_progress = {}

async def send_quiz_sequence(user_id):
    q_idx = quiz_progress.get(user_id, 0)
    if q_idx < len(questions):
        q = questions[q_idx]
        markup = InlineKeyboardMarkup()
        for option in q["options"].keys():
            markup.add(InlineKeyboardButton(option, callback_data=f"quiz_{q_idx}_{option}"))
        await bot.send_message(user_id, q["text"], reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("quiz_"))
async def handle_quiz_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    parts = callback_query.data.split("_", 2)
    if len(parts) < 3:
        await callback_query.answer("🤔 Неизвестный ответ")
        return

    q_idx_str, selected = parts[1], parts[2]
    try:
        q_idx = int(q_idx_str)
    except ValueError:
        await callback_query.answer("🤔 Неизвестный ответ")
        return

    if q_idx >= len(questions):
        await callback_query.answer("🧠 Викторина уже завершена.")
        return

    if quiz_progress.get(user_id, 0) > q_idx:
        await callback_query.answer("🔁 Этот вопрос уже пройден")
        return
        
        question = questions[q_idx]

    if selected in question["options"]:
        is_correct, comment = question["options"][selected]
        await callback_query.answer()
        await bot.send_message(user_id, comment)

        if is_correct:
            quiz_progress[user_id] = q_idx + 1
            await asyncio.sleep(1)
            if quiz_progress[user_id] < len(questions):
                await send_quiz_sequence(user_id)
            else:
                await bot.send_message(user_id, "🎉 Ты прошёл все вопросы! 🎁")
                await handle_quiz_completion(user_id)
        else:
            await bot.send_message(user_id, "❌ Нет, не так! Попробуй ещё раз.")
    else:
        await callback_query.answer("🤔 Неизвестный ответ")


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

async def on_startup(dp):
    asyncio.create_task(send_hourly_compliments())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
