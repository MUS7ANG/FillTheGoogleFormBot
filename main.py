import asyncio
import time
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from selenium import webdriver
from selenium.webdriver.common.by import By
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import ntplib

TOKEN = "7623595891:AAFVppQGyjImFUfK3rGsnUPq1k_ky5WHd_A"
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

user_data = {}


def get_exact_time():
    client = ntplib.NTPClient()
    response = client.request("pool.ntp.org", version=3)
    return response.tx_time


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Отправь мне ссылку на Google Форму.")


@dp.message()
async def get_form(message: Message):
    user_id = message.from_user.id

    if "docs.google.com/forms" in message.text:
        user_data[user_id] = {"form_url": message.text}
        await message.answer("Принял! Сколько полей нужно заполнить?")

    elif message.text.isdigit():
        user_data[user_id]["field_count"] = int(message.text)
        user_data[user_id]["answers"] = []
        await message.answer(
            f"Окей! Введи {user_data[user_id]['field_count']} ответов (каждый отправь отдельным сообщением).")

    elif user_id in user_data and "field_count" in user_data[user_id]:
        user_data[user_id]["answers"].append(message.text)

        if len(user_data[user_id]["answers"]) == user_data[user_id]["field_count"]:
            await message.answer("Теперь введи время отправки (ЧЧ:ММ:СС)")

    elif ":" in message.text and message.text.count(":") == 2:
        user_data[user_id]["time"] = message.text
        await message.answer("Отлично! Ожидаю точного времени...")

        hours, minutes, seconds = map(int, message.text.split(":"))
        now = datetime.now()
        run_time = datetime(now.year, now.month, now.day, hours, minutes, seconds)

        scheduler.add_job(fill_form, "date", run_date=run_time, args=[user_id])
        scheduler.start()


async def fill_form(user_id):
    form_url = user_data[user_id]["form_url"]
    answers = user_data[user_id]["answers"]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(form_url)
    time.sleep(2)

    target_time = get_exact_time() + 3
    while get_exact_time() < target_time - 0.1:
        time.sleep(0.01)

    inputs = driver.find_elements(By.XPATH, '//input[@type="text"]')
    for i, answer in enumerate(answers):
        if i < len(inputs):
            inputs[i].send_keys(answer)

    submit_button = driver.find_element(By.XPATH, '//span[text()="Отправить"]')
    submit_button.click()

    driver.quit()
    await bot.send_message(user_id, "✅ Форма отправлена ровно в указанное время!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())