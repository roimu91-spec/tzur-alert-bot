import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8457356709:AAEZz6CObKzeLsHjKbCHkYGumJNlR8tX42c״
CHAT_ID = -1003864517348

AREAS = [
    "צור יצחק",
    "דרום השרון",
    "יישובי דרום השרון",
    "השרון"
]

sent_ids = set()


# ===============================
# פיקוד העורף
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
            if isinstance(data, list):
                return data

        return []

    except Exception as e:
        print("OREF ERROR:", e)
        return []


# ===============================
# גיבוי
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
# לולאת בדיקה
# ===============================
async def check_alerts(app):
    while True:
        try:
            alerts = get_oref()

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

                msg = f"🚨 אזעקה!\n{', '.join(cities)}"

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
# START COMMAND
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("הבוט עובד ✅")


# ===============================
# INIT
# ===============================
async def post_init(app):
    asyncio.create_task(check_alerts(app))


def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # 🔥 חשוב מאוד
    app.add_handler(CommandHandler("start", start))

    print("Bot started 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
