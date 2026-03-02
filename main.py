import requests
import time
import os
from telegram import Bot

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CITY_NAME = "צור יצחק"

bot = Bot(token=TOKEN)

last_alert_id = None

def check_alerts():
    global last_alert_id

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(
            "https://www.oref.org.il/WarningMessages/alert/alerts.json",
            headers=headers,
            timeout=5
        )

        if r.status_code == 200:
            data = r.json()

            if data and "data" in data and data["data"]:
                cities = data["data"]
                alert_id = data.get("id")
                title = data.get("title", "")

                if CITY_NAME in cities and alert_id != last_alert_id:
                    if "חזרה לשגרה" in title:
                        bot.send_message(chat_id=CHAT_ID, text="✅ חזרה לשגרה בצור יצחק")
                    else:
                        bot.send_message(chat_id=CHAT_ID, text="🚨 אזעקה בצור יצחק!")

                    last_alert_id = alert_id

    except:
        pass

while True:
    check_alerts()
    time.sleep(3)
