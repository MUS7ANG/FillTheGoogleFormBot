import pytz

FIREFOX_OPTIONS = [
    "-headless",  # Запуск в headless-режиме
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-extensions"
]

# Часовой пояс Бишкека
BISHKEK_TZ = pytz.timezone("Asia/Bishkek")

#BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_TOKEN = '7803855448:AAGmIMoPz2Dnd27XZZlihBD5hyJuP7DYhJw'
NTP_SERVER = "pool.ntp.org"