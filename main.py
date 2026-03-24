import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

TARGET_CITIES = ["צור יצחק", "כפר סבא"]

last_alert_id = None


# ===============================
# קבלת נתונים (Red Alert API)
# ===============================
def get_alerts():
    try:
        url = "https://api.tzevaadom.co.il/notifications"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            return res.json()
        else:
            print("ERROR:", res.status_code)
            return []

    except Exception as e:
        print("EXCEPTION:", e)
        return []


# ===============================
# סינון ערים
# ===============================
def filter_cities(cities):
    result = []
    for city in cities:
        for target in TARGET_CITIES:
            if target in city:
                result.append(city)
    return result


# ===============================
# בדיקה ושליחה
# ===============================
async def check_alerts(app):
    global last_alert_id

    while True:
        try:
            alerts = get_alerts()

            print("DATA:", alerts)

            if alerts:
                for alert in alerts:

                    alert_id = alert.get("notificationId")

                    # לא לשלוח שוב אותו דבר
                    if alert_id == last_alert_id:
                        continue

                    cities = alert.get("cities", [])
                    filtered = filter_cities(cities)

                    if filtered:
                        message = "🚨 אזעקה!\n" + ", ".join(filtered)

                        print("🚨 שולח:", message)

                        await app.bot.send_message(
                            chat_id=CHAT_ID,
                            text=message
                        )

                        last_alert_id = alert_id

        except Exception as e:
            print("MAIN ERROR:", e)

        await asyncio.sleep(2)


# ===============================
# פקודות
# ===============================
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט עובד")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 הבוט פעיל ומנטר אזעקות")


# ===============================
# MAIN
# ===============================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("status", status))

    print("Bot started 🚀")

    asyncio.create_task(check_alerts(app))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
