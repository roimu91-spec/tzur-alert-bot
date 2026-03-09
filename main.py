import requests
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITY_NAME = "צור יצחק"

last_alert_id = None


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל ועובד.")


def get_alerts():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.oref.org.il/"
    }

    sources = [
        "https://www.oref.org.il/WarningMessages/alert/alerts.json",
        "https://api.oref.org.il/alerts.json"
    ]

    for url in sources:

        try:
            r = requests.get(url, headers=headers, timeout=5)

            if r.status_code == 200:

                data = r.json()

                if isinstance(data, dict) and "data" in data:
                    return data

        except:
            continue

    return None


async def check_alerts(app):

    global last_alert_id

    while True:

        try:

            data = get_alerts()

            if data:

                cities = data.get("data", [])
                alert_id = data.get("id")

                if cities and alert_id != last_alert_id:

                    for city in cities:

                        if CITY_NAME in city:

                            await app.bot.send_message(
                                chat_id=CHAT_ID,
                                text="🚨 אזעקה בצור יצחק!\n\n"
                                     "הנחיות פיקוד העורף:\n"
                                     "• להיכנס מיד למרחב מוגן\n"
                                     "• להישאר לפחות 10 דקות"
                            )

                            last_alert_id = alert_id

        except Exception as e:

            print("Error:", e)

        await asyncio.sleep(1)


async def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(check_alerts(app))

    print("Bot started")

    await app.run_polling()


if __name__ == "__main__":

    asyncio.run(main())
