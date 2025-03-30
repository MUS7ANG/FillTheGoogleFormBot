import os
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "7623595891:AAFVppQGyjImFUfK3rGsnUPq1k_ky5WHd_A")

NTP_SERVER = "asia.pool.ntp.org"

BISHKEK_TZ = timezone("Asia/Bishkek")

CHROME_OPTIONS = ["--headless"]