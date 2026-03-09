import requests
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITY_NAME = "צור יצחק"

last_alert = None


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל.")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 בדיקת אזעקה בצור יצחק")


def get_oref_alerts():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.oref.org.il/"
    }

    url = "https://www.oref.org.il/WarningMessages/alert/alerts.json"

    try:

        r = requests.get(url, headers=headers, timeout=5)

        if r.status_code == 200:

            data = r.json()

            if "data" in data:
                return data["data"]

    except:
        return []


def get_redalert():

    url = "https://api.tzevaadom.co.il/notifications"

    try:

        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            return r.json()

    except:
        return []

    return []


async def check_alerts(app):

    global last_alert

    while True:

        try:

            cities = []

            # פיקוד העורף
            oref = get_oref_alerts()

            if oref:
                cities.extend(oref)

            # red alert
            red = get_redalert()

            if red:
                cities.extend(red)

            if cities:

                if CITY_NAME in str(cities) and cities != last_alert:

                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text="🚨 אזעקה בצור יצחק!\n\n"
                             "היכנס מיד למרחב מוגן\n"
                             "הישאר לפחות 10 דקות"
                    )

                    last_alert = cities

        except Exception as e:

            print("Error:", e)

        await asyncio.sleep(1)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))

    asyncio.get_event_loop().create_task(check_alerts(app))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
