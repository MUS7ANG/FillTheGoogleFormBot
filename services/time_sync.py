import ntplib
from config.config import NTP_SERVER, BISHKEK_TZ
from datetime import datetime
from pytz import timezone

def get_exact_time():
    client = ntplib.NTPClient()
    response = client.request(NTP_SERVER, version=3)
    return response.tx_time

def get_bishkek_time():
    utc_time = datetime.fromtimestamp(get_exact_time(), tz=timezone("UTC"))
    return utc_time.astimezone(BISHKEK_TZ)