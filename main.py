import requests
import asyncio
from telegram import Bot

TOKEN = "8457356709:AAGtwHiQHvYQww9KPIQwdLpddsIYIJ-wAkc"
CHAT_ID = "-1003864517348"

bot = Bot(token=TOKEN)

last_ids = set()

TARGET_CITIES = ["צור יצחק", "כפר סבא", "צור יגאל", "כוכב יאיר", "טייבה", "טירה", "אייל", "סלעית"]

def get_alerts():
    try:
        url = "https://api.tzevaadom.co.il/notifications"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

async def main():
    print("Bot started 🚀")

    while True:
        try:
            data = get_alerts()

            if data:
                for alert in data:
                    alert_id = alert.get("notificationId")

                    if alert_id in last_ids:
                        continue

                    cities = alert.get("cities", [])

                    filtered = [
                        city for city in cities
                        if any(city == target or city.startswith(target + " ") for target in TARGET_CITIES)
                    ]

                    if filtered:
                        text = "🚨 אזעקה!\n" + ", ".join(filtered)

                        await bot.send_message(
                            chat_id=CHAT_ID,
                            text=text
                        )

                        last_ids.add(alert_id)

            await asyncio.sleep(2)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
