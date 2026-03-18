import requests
import os
from telegram import Bot
from telegram.ext import Updater, CommandHandler

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CITY_NAME = "צור יצחק"

bot = Bot(token=TOKEN)
last_alert = None


# ===== פקודות =====

def status(update, context):
    update.message.reply_text("✅ הבוט פעיל")


def test(update, context):
    bot.send_message(
        chat_id=CHAT_ID,
        text="🚨 בדיקת אזעקה (test)"
    )


# ===== מקורות =====

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
            return r.json().get("data", [])

    except Exception as e:
        print("OREF ERROR:", e)

    return []


def get_redalert():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(
            "https://api.redalert.me/alerts.json",
            headers=headers,
            timeout=5
        )

        if r.status_code == 200:
            return r.json()

    except Exception as e:
        print("RED ERROR:", e)

    return []


# ===== בדיקה אחת =====

def check_alerts_once():
    global last_alert

    try:
        oref_data = get_oref()
        red_data = get_redalert()

        print("OREF:", oref_data)
        print("RED:", red_data)

        found = False

        # בדיקה גמישה (לא התאמה מדויקת)
        for item in oref_data:
            if CITY_NAME in str(item):
                found = True

        if red_data:
            for item in red_data:
                if CITY_NAME in str(item):
                    found = True

        if found and last_alert != "alert":
            bot.send_message(
                chat_id=CHAT_ID,
                text="🚨 אזעקה בצור יצחק!\nהיכנס למרחב מוגן מיד!"
            )
            last_alert = "alert"

        if not found:
            last_alert = None

    except Exception as e:
        print("CHECK ERROR:", e)


# ===== חיבור ל-job queue =====

def run_check(context):
    check_alerts_once()


# ===== הפעלה =====

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("test", test))

    print("Bot started")

    # הרצה כל 2 שניות (יציב!)
    job_queue = updater.job_queue
    job_queue.run_repeating(run_check, interval=2, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
