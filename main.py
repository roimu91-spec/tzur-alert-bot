import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8457356709:AAEZz6C0bKzeLsHjKbCHkYGumJNlR8tX42c"
CHAT_ID = "-1003864517348"

TARGET_CITIES = ["צור יצחק", "כפר סבא"]

last_ids = set()

def get_alerts():
    try:
        res = requests.get("https://api.tzevaadom.co.il/notifications", timeout=5)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

def filter_cities(cities):
    return [c for c in cities if any(t in c for t in TARGET_CITIES)]

async def check(app):
    global last_ids
    while True:
        try:
            alerts = get_alerts()
            for a in alerts:
                aid = a.get("notificationId")
                if not aid or aid in last_ids:
                    continue
                cities = filter_cities(a.get("cities", []))
                if cities:
                    await app.bot.send_message(chat_id=CHAT_ID, text="🚨 אזעקה!\n" + ", ".join(cities))
                    last_ids.add(aid)
                    if len(last_ids) > 50:
                        last_ids = set(list(last_ids)[-20:])
        except:
            pass
        await asyncio.sleep(2)

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="✅ עובד")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 פעיל")

async def start(app):
    asyncio.create_task(check(app))

def main():
    app = ApplicationBuilder().token(TOKEN).post_init(start).build()
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()

if __name__ == "__main__":
    main()
