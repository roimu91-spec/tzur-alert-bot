import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITY_NAME = "צור יצחק"

last_alert = None


# סטטוס
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל")


# בדיקה
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="🚨 בדיקה לערוץ צור יצחק"
    )


# 🚨 בדיקת אזעקות (RedAlert)
async def check_alerts(app):

    global last_alert

    while True:
        try:
            r = requests.get(
                "https://api.tzevaadom.co.il/notifications",
                timeout=5
            )

            if r.status_code == 200:

                data = r.json()
                print("DATA:", data)

                if data:

                    alert_id = str(data)

                    if alert_id != last_alert:

                        cities = data[0].get("cities", [])

                        print("Cities:", cities)

                        for city in cities:
                            if "צור יצחק" in city:

                                print("🚨 ALERT DETECTED")

                                await app.bot.send_message(
                                    chat_id=CHAT_ID,
                                    text="🚨 אזעקה בצור יצחק!\n\nהיכנסו מיד למרחב מוגן!"
                                )

                                last_alert = alert_id

        except Exception as e:
            print("ERROR:", e)

        await asyncio.sleep(2)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))

    async def start_tasks(app):
        asyncio.create_task(check_alerts(app))

    app.post_init = start_tasks

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
