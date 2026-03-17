import asyncio
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CITY_NAME = "צור יצחק"

last_alert = None


# ===== פקודות =====

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="🚨 בדיקת אזעקה (test)"
    )


# ===== מקור 1 - פיקוד העורף =====

def get_oref():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.oref.org.il/",
            "X-Requested-With": "XMLHttpRequest"
        }

        r = requests.get(
            "https://www.oref.org.il/WarningMessages/alert/alerts.json",
            headers=headers,
            timeout=5
        )

        if r.status_code == 200:
            data = r.json()
            return data.get("data", [])
        return []

    except Exception as e:
        print("OREF ERROR:", e)
        return []


# ===== מקור 2 - RedAlert =====

def get_redalert():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(
            "https://api.redalert.me/alerts.json",
            headers=headers,
            timeout=5
        )

        if r.status_code == 200:
            return r.json()

        return []

    except Exception as e:
        print("RED ERROR:", e)
        return []


# ===== בדיקה מרכזית =====

async def check_alerts(app):
    global last_alert

    while True:
        try:
            oref_data = get_oref()
            red_data = get_redalert()

            print("OREF:", oref_data)
            print("RED:", red_data)

            found = False

            # בדיקה בפיקוד העורף
            if isinstance(oref_data, list) and CITY_NAME in oref_data:
                found = True

            # בדיקה ב-RedAlert (עם הגנה מקריסה)
            if red_data:
                try:
                    for item in red_data:
                        if CITY_NAME in str(item):
                            found = True
                except:
                    pass

            # שליחת אזעקה
            if found and last_alert != "alert":
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text="🚨 אזעקה בצור יצחק!\nהיכנס למרחב מוגן מיד!"
                )
                last_alert = "alert"

            # איפוס
            if not found:
                last_alert = None

        except Exception as e:
            print("MAIN ERROR:", e)

        await asyncio.sleep(2)


# ===== MAIN =====

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test))

    asyncio.create_task(check_alerts(app))

    print("Bot started")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
