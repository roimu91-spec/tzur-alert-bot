import requests
import time
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CITY_NAME = "צור יצחק"

last_alert_id = None


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל ועובד.")


async def check_alerts(app):
    global last_alert_id

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.oref.org.il/",
        "X-Requested-With": "XMLHttpRequest"
    }

    while True:
        try:
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

                            await app.bot.send_message(
                                chat_id=CHAT_ID,
                                text="✅ חזרה לשגרה בצור יצחק\nאפשר לצאת מהמרחב המוגן."
                            )

                        else:

                            await app.bot.send_message(
                                chat_id=CHAT_ID,
                                text="🚨 אזעקה בצור יצחק!\n\n"
                                     "הנחיות פיקוד העורף:\n"
                                     "• להיכנס מיד למרחב מוגן\n"
                                     "• לסגור דלת וחלון\n"
                                     "• להישאר במרחב המוגן לפחות 10 דקות\n"
                                     "• להמתין להודעה על חזרה לשגרה"
                            )

                        last_alert_id = alert_id

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(2)


import asyncio


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(check_alerts(app))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
