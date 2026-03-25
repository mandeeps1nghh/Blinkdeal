import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MYNTRA_URL = "https://www.myntra.com/gold-coin?src=bc"


def send_telegram_alert(deal_data):
    """Send a Telegram message about the active BlinkDeal."""
    coupon = deal_data.get("coupon_code") or "N/A"
    discount = deal_data.get("discount") or "N/A"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"\U0001f525 BlinkDeal LIVE on Myntra!\n\n"
        f"Coupon: {coupon}\n"
        f"Discount: {discount}\n"
        f"Time: {timestamp}\n"
        f"Link: {MYNTRA_URL}"
    )

    if not BOT_TOKEN or not CHAT_ID:
        print(f"[Alerter] Telegram creds not set. Message:\n{message}")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("[Alerter] Telegram alert sent successfully!")
            return True
        else:
            print(f"[Alerter] Telegram API error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[Alerter] Failed to send Telegram alert: {e}")
        return False
