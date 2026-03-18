import requests
import asyncio
from telegram import Bot

TOKEN = "8457356709:AAFgmuKCiJHk_IrNOMOUdLgVDi95wDfrG08"
CHAT_ID = "-1003864517348"

bot = Bot(token=TOKEN)

last_alert = None


# ===============================
# OREF (פיקוד העורף)
# ===============================
def get_oref():
    try:
        url = "https://www.oref.org.il/WarningMessages/alert/alerts.json"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.oref.org.il/",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest"
        }

        res = requests.get(url, headers=headers, timeout=5)

        if res.status_code == 200:
            return res.json()
        else:
            print("OREF ERROR:", res.status_code)
            return None

    except Exception as e:
        print("OREF EXCEPTION:", e)
        return None


# ===============================
# Red Alert (גיבוי)
# ===============================
def get_red():
    try:
        url = "https://api.tzevaadom.co.il/notifications"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            return res.json()
        else:
            print("RED ERROR:", res.status_code)
            return None

    except Exception as e:
        print("RED EXCEPTION:", e)
        return None


# ===============================
# בדיקה ושליחה
# ===============================
async def check_alerts():
    global last_alert

    while True:
        try:
            oref = get_oref()
            red = get_red()

            print("OREF:", oref)
            print("RED:", red)

            alert_data = None

            # ===== OREF =====
            if isinstance(oref, dict) and "data" in oref and oref["data"]:
                cities = ", ".join(oref["data"])
                alert_data = f"🚨 אזעקה!\nאזורים: {cities}"

            # ===== RED =====
            elif isinstance(red, list) and len(red) > 0:
                alert_data = f"🚨 אזעקה (גיבוי)\n{red}"

            # ===== שליחה =====
            if alert_data and alert_data != last_alert:
                print("🚨 שולח לטלגרם")

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=alert_data
                )

                last_alert = alert_data

        except Exception as e:
            print("MAIN ERROR:", e)

        await asyncio.sleep(2)


# ===============================
# הרצה
# ===============================
async def main():
    print("Bot started 🚀")
    await check_alerts()


if __name__ == "__main__":
    asyncio.run(main())
