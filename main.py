import requests
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8457356709:AAFgmuKCiJHk_IrNOMOUdLgVDi95wDfrG08"
CHAT_ID = "-1003864517348"

MY_AREAS = ["צור יצחק"]

sent_ids = set()


# ===============================
# RED ALERT
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
# פקודות
# ===============================
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט עובד!")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📡 סטטוס:\n"
        f"מעקב אחרי: {', '.join(MY_AREAS)}\n"
        f"אזעקות שנשלחו: {len(sent_ids)}"
    )


# ===============================
# בדיקת אזעקות
# ===============================
async def check_alerts(app):
    while True:
        try:
            red = get_red()
            print("RED:", red)

            for alert in red:
                alert_id = alert.get("notificationId")
                cities = alert.get("cities", [])

                matched = [c for c in cities if c in MY_AREAS]

                if matched and alert_id not in sent_ids:
                    msg = f"🚨 אזעקה בצור יצחק!\n{', '.join(matched)}"

                    await app.bot.send_message(chat_id=CHAT_ID, text=msg)
                    print("🚨 נשלח")

                    sent_ids.add(alert_id)

        except Exception as e:
            print("MAIN ERROR:", e)

        await asyncio.sleep(2)


# ===============================
# MAIN
# ===============================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(check_alerts(app))

    print("Bot started 🚀")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
