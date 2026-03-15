import os
import asyncio
import json
import requests
import websocket
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITY = "צור יצחק"

last_alert = None


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 בדיקת אזעקה בצור יצחק")


def get_redalert():

    url = "https://api.tzevaadom.co.il/notifications"

    try:

        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            return r.json()

    except:
        return []

    return []


def get_oref():

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

    return []


async def check_alerts(app):

    global last_alert

    while True:

        try:

            cities = []

            red = get_redalert()

            if red:
                cities.extend(red)

            oref = get_oref()

            if oref:
                cities.extend(oref)

            if cities:

                if CITY in str(cities) and cities != last_alert:

                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text="🚨 אזעקה בצור יצחק!\n\n"
                             "היכנס מיד למרחב מוגן\n"
                             "הישאר לפחות 10 דקות"
                    )

                    last_alert = cities

        except Exception as e:

            print(e)

        await asyncio.sleep(1)


def websocket_listener(app):

    def on_message(ws, message):

        try:

            data = json.loads(message)

            if CITY in str(data):

                asyncio.run(
                    app.bot.send_message(
                        chat_id=CHAT_ID,
                        text="⚠️ ייתכן ירי לכיוון אזור צור יצחק"
                    )
                )

        except:
            pass

    ws = websocket.WebSocketApp(
        "wss://redalert.il/api/websocket",
        on_message=on_message
    )

    ws.run_forever()


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))

    asyncio.get_event_loop().create_task(check_alerts(app))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
