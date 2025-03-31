import os
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "7803855448:AAGmIMoPz2Dnd27XZZlihBD5hyJuP7DYhJw")

NTP_SERVER = "asia.pool.ntp.org"

BISHKEK_TZ = timezone("Asia/Bishkek")

CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-extensions",
    "--no-first-run",
    "--disable-background-networking"
]