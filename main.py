import requests
import asyncio
from telegram.ext import ApplicationBuilder

TOKEN = "8457356709:AAFgmuKCiJHk_IrNOMOUdLgVDi95wDfrG08"
CHAT_ID = -1003864517348

AREAS = [
    "צור יצחק",
    "דרום השרון",
    "יישובי דרום השרון",
    "השרון"
]

sent_ids = set()


# ===============================
# מקור 1 - פיקוד העורף (הכי אמין)
# ===============================
def get_oref():
    try:
        url = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.oref.org.il/"
        }

        res = requests.get(url, headers=headers, timeout=5)

        if res.status_code == 200:
            data = res.json()

            # אם אין אזעקות זה מחזיר []
            if isinstance(data, list):
                return data

        return []

    except Exception as e:
        print("OREF ERROR:", e)
        return []


# ===============================
# מקור 2 - גיבוי (כמו צופר)
# ===============================
def get_red():
    try:
        url = "https://api.tzevaadom.co.il/notifications"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            return res.json()

        return []

    except Exception as e:
        print("RED ERROR:", e)
        return []


# ===============================
# סינון אזורים
# ===============================
def is_relevant(cities):
    for city in cities:
        for area in AREAS:
            if area in city:
                return True
    return False


# ===============================
# לולאה ראשית
# ===============================
async def check_alerts(app):
    while True:
        try:
            # קודם OREF (מהיר ואמין)
            alerts = get_oref()

            # אם ריק → נסה RED
            if not alerts:
                alerts = get_red()

            print("DATA:", alerts)

            for alert in alerts:
                alert_id = alert.get("notificationId") or str(alert)

                if alert_id in sent_ids:
                    continue

                cities = alert.get("cities", []) if isinstance(alert, dict) else []

                if not is_relevant(cities):
                    continue

                msg = f"🚨 אזעקה בצור יצחק!\n{', '.join(cities)}"

                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg
                )

                print("🚨 נשלח!")
                sent_ids.add(alert_id)

        except Exception as e:
            print("MAIN ERROR:", e)

        await asyncio.sleep(2)


# ===============================
# MAIN
# ===============================
async def post_init(app):
    asyncio.create_task(check_alerts(app))


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    print("Bot started 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
