import ntplib
import pytz
import requests

from config.config import NTP_SERVER, BISHKEK_TZ
from datetime import datetime
from pytz import timezone

def get_exact_time():
    client = ntplib.NTPClient()
    response = client.request(NTP_SERVER, version=3)
    return response.tx_time

def get_bishkek_time():
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Bishkek")
        data = response.json()
        dt = datetime.fromisoformat(data["datetime"].split(".")[0])
        return pytz.timezone("Asia/Bishkek").localize(dt)
    except Exception as e:
        print(f"Ошибка при получении времени: {e}")
        return datetime.now(pytz.timezone("Asia/Bishkek"))