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