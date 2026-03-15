import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITY_NAME = "צור יצחק"

last_alert_id = None


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="🚨 בדיקת אזעקה בצור יצחק"
    )


async def check_alerts(app):
    global last_alert_id

    headers = {
        "User-Agent": "Mozilla/5.0"
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

                    if CITY_NAME in cities and alert_id != last_alert_id:

                        await app.bot.send_message(
                            chat_id=CHAT_ID,
                            text="🚨 אזעקה בצור יצחק!\nהיכנסו מיד למרחב מוגן!"
                        )

                        last_alert_id = alert_id

        except Exception as e:
            print("Alert error:", e)

        await asyncio.sleep(3)


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
