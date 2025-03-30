from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.form_filler import fill_form
from config.config import BISHKEK_TZ
from services.time_sync import get_bishkek_time

user_data = {}
scheduler = AsyncIOScheduler()

def register_handlers(dp: Dispatcher, bot: Bot):

    @dp.message(Command("start"))
    async def start(message: Message):
        print(f"Получена команда /start от {message.from_user.id}")
        await message.answer("Привет! Отправь мне ссылку на Google Форму.")

    @dp.message()
    async def get_form(message: Message):
        user_id = message.from_user.id
        print(f"Получено сообщение от {user_id}: {message.text}")

        if "docs.google.com/forms" in message.text:
            user_data[user_id] = {"form_url": message.text}
            await message.answer("Принял! Сколько полей нужно заполнить?")
            print(f"Сохранён URL формы для {user_id}")

        elif message.text.isdigit() and user_id in user_data and "form_url" in user_data[user_id]:
            user_data[user_id]["field_count"] = int(message.text)
            user_data[user_id]["answers"] = []
            await message.answer(
                f"Окей! Введи {user_data[user_id]['field_count']} ответов (каждый отправь отдельным сообщением)."
            )
            print(f"Установлено количество полей: {user_data[user_id]['field_count']}")

        elif user_id in user_data and "field_count" in user_data[user_id] and \
                len(user_data[user_id]["answers"]) == user_data[user_id]["field_count"] and \
                ":" in message.text and message.text.count(":") == 2:
            try:
                user_data[user_id]["time"] = message.text
                await message.answer("Отлично! Ожидаю точного времени в Бишкеке...")
                print(f"Установлено время отправки: {message.text}")

                hours, minutes, seconds = map(int, message.text.split(":"))
                print(f"Распарсено время: {hours}:{minutes}:{seconds}")

                now_bishkek = get_bishkek_time()
                print(f"Текущее время в Бишкеке: {now_bishkek}")

                run_time_naive = datetime(now_bishkek.year, now_bishkek.month, now_bishkek.day,
                                          hours, minutes, seconds)
                run_time = BISHKEK_TZ.localize(run_time_naive)
                print(f"Время выполнения (до проверки): {run_time}")

                if run_time < now_bishkek:
                    run_time = run_time.replace(day=run_time.day + 1)
                print(f"Окончательное время выполнения: {run_time}")

                scheduler.add_job(
                    fill_form,
                    "date",
                    run_date=run_time,
                    args=[bot, user_id, user_data[user_id]["form_url"], user_data[user_id]["answers"]]
                )
                print("Задача успешно добавлена в scheduler.")
            except ValueError as e:
                print(f"Ошибка парсинга времени: {str(e)}")
                await message.answer("Ошибка: введите время в формате ЧЧ:ММ:СС (например, 14:30:00)")
            except Exception as e:
                print(f"Неизвестная ошибка при планировании: {str(e)}")
                await message.answer(f"Произошла ошибка: {str(e)}")

        elif user_id in user_data and "field_count" in user_data[user_id] and \
             len(user_data[user_id]["answers"]) < user_data[user_id]["field_count"]:
            user_data[user_id]["answers"].append(message.text)
            print(f"Добавлен ответ: {message.text}. Всего: {len(user_data[user_id]['answers'])}/{user_data[user_id]['field_count']}")
            if len(user_data[user_id]["answers"]) == user_data[user_id]["field_count"]:
                await message.answer("Теперь введи время отправки по Бишкеку (ЧЧ:ММ:СС)")