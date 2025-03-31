import asyncio
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from handlers.telegram import register_handlers, scheduler

async def main():
    print("Запуск бота...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    print("Регистрация обработчиков...")
    register_handlers(dp, bot)

    print("Планировщик запускается...")
    scheduler.start()
    print("Планировщик активен:", scheduler.running)

    async def reset_webhook():
        await bot.delete_webhook()
        await bot.session.close()

    asyncio.run(reset_webhook())
    print("Бот начал опрос Telegram API.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())