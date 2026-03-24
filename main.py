import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8457356709:AAEZz6C0bKzeLsHjKbCHkYGumJNlR8tX42c"
CHAT_ID = "-1003864517348"

TARGET_CITIES = ["צור יצחק", "כפר סבא"]

last_alert_id = None

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

async def check_alerts(app):
    global last_alert_id
    while True:
        try:
            alerts = get_alerts()
            for alert in alerts:
                alert_id = alert.get("notificationId")
                if not alert_id or alert_id == last_alert_id:
                    continue
                cities = alert.get("cities", [])
                filtered = filter_cities(cities)
                if filtered:
                    msg = "🚨 אזעקה!\n" + ", ".join(filtered)
                    await app.bot.send_message(chat_id=CHAT_ID, text=msg)
                    last_alert_id = alert_id
        except:
            pass
        await asyncio.sleep(2)

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="✅ עובד")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 פעיל")

async def post_init(app):
    asyncio.create_task(check_alerts(app))

def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()

if __name__ == "__main__":
    main()
