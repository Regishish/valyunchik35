    # -*- coding: utf-8 -*-
import os
import logging
import asyncio
    from aiogram import Bot, Dispatcher, types
    from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
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
        {"text": "🍹 Задание 5: Время аперитива и вкусного обеда! С тебя селфи с бокалом пива/негрони/апероля/чего захочешь!"},
        {"text": "💃 Задание 6: Включи свою любимую песню и потанцуй. В качестве пруфов — жена должна видеть!"},
        {"text": "🍽️ Задание 7: Выбери ресторан на вечер, где мы отпразднуем твоё 35-летие:\n1. Восточный квартал\n2. СанРемо\n3. Плакучая Ива\n4. Чита-Маргарита\n5. Реззо\n6. Свой вариант"}
    ]
    
    user_states = {}
    quiz_progress = {}
    
    @dp.message_handler(commands=['start'])
    async def start_game(message: types.Message):
        if message.from_user.id in USER_IDS:
            user_states[message.from_user.id] = 0
            await message.answer("🎉 Поздравляю, ты в игре! Сегодня тебя ждёт несколько заданий, а в конце — подарочек.")
            await send_next_quest(message.from_user.id)
    
    async def send_next_quest(user_id):
        index = user_states.get(user_id, 0)
        if index < len(QUESTS):
            quest_text = QUESTS[index]["text"]
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Готово", callback_data="task_done")
            )
            await bot.send_message(user_id, quest_text, reply_markup=markup)
        elif index == len(QUESTS):  # после последнего квеста
            await bot.send_message(user_id, "🎯 Теперь — мини-викторина 😊")
            quiz_progress[user_id] = 0  # <--- обязательно инициализируем индекс!
            await send_quiz_sequence(user_id)
    
    @dp.message_handler(content_types=types.ContentType.ANY)
    async def handle_user_response(message: types.Message):
        if message.from_user.id in USER_IDS:
            state = user_states.get(message.from_user.id, 0)
            if state < len(QUESTS):
                user_states[message.from_user.id] += 1
                await send_next_quest(message.from_user.id)
            elif state == len(QUESTS):
                # Если пользователь прислал ещё сообщение на старое задание — просто проигнорировать
                pass
    
                # Похвалы после каждого задания
                compliments = [
        "🥐 Завтрак выглядит так, что Michelin бы позавидовал! Красиво, сытно — ты задал дню правильный вкус.",
        "📞 Отлично, спасибо! Это было важно. Теперь у нас с тобой +100 к карме и маминому расположению 💕",
        "🎂 Это волшебный торт, волшебный день — и желание? Ну оно просто обязано сбыться!",
        "🏖️ На этом пляже ты как и на любом другом — статный Апполон в своей стихии!",
        "🍹 Отличный выбор, Чин-чин! Пусть в этом бокале будет вся лёгкость и радость дня!",
        "🕺 Ты — звезда танцпола, даже если танцпол — это балкон! Настроение на максимум?",
        "🍽️ Я за любой твой выбор, особенно если мы идём туда вместе ❤️"
    ]
    
    @dp.message_handler(content_types=types.ContentType.ANY)
    async def handle_user_response(message: types.Message):
        if message.from_user.id in USER_IDS:
            state = user_states.get(message.from_user.id, 0)
            if state < len(QUESTS):
                await message.reply(f"✅ Задание выполнено!\n{compliments[state]}")
                user_states[message.from_user.id] += 1
                await send_next_quest(message.from_user.id)
    
    
    async def send_quiz_sequence(user_id):
        q_idx = quiz_progress.get(user_id, 0)
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
                    "За всё это вместе": (True, "✅ Вот оно, сердце моё 💖")
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
            markup = types.InlineKeyboardMarkup()
            for option in q["options"].keys():
                markup.add(types.InlineKeyboardButton(option, callback_data=f"quiz_{option}"))
            await bot.send_message(user_id, q["text"], reply_markup=markup)
    @dp.callback_query_handler(lambda c: c.data.startswith("quiz_"))
    async def handle_quiz_answer(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        q_idx = quiz_progress.get(user_id, 0)
        selected = callback_query.data.replace("quiz_", "")
        q = questions[q_idx]
    
        is_correct, comment = q["options"].get(selected, (False, "🤔 Неизвестный ответ"))
        await bot.answer_callback_query(callback_query.id, text=comment)
    
        if is_correct:
            quiz_progress[user_id] = q_idx + 1
            if quiz_progress[user_id] < len(questions):
                await send_quiz_sequence(user_id)
            else:
                await bot.send_message(user_id, "🎉 Ты прошёл все вопросы! Остался последний квест.")
                await bot.send_message(user_id, "💃 Включи музыку и танцуй. Главное — чтобы жена видела 🕺")
    
        if is_correct:
            if q_idx + 1 < len(questions):
                quiz_progress[user_id] = q_idx + 1
                await send_quiz_sequence(user_id)
        else:
                await bot.send_message(user_id, "🎉 Ты прошёл все вопросы! Финальный код: 1335")
                user_states[user_id] += 1
                await send_next_quest(user_id)
    
        if condition:
                await bot.send_message(...)
        else:
                await bot.send_message(...)
    
                await bot.send_message(user_id, "🎉 Поздравляю, ты прошёл опрос! Ты почти у цели… Скоро тебя ждёт кое-что очень приятное 🎁❤️")
                await bot.send_message(user_id, """💃 А теперь — бонусное задание! Включи свою любимую песню и потанцуй 🕺
    👁️‍🗨️ Важно: жена должна видеть! Потом уже — подарок 🎁""")
    
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
