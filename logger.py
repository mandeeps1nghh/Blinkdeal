import csv
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "deals.csv")


def log_deal(deal_data):
    """Append a deal record to the CSV log."""
    file_exists = os.path.exists(LOG_FILE)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coupon_code": deal_data.get("coupon_code") or "",
        "discount": deal_data.get("discount") or "",
        "status": "active" if deal_data.get("deal_active") else "inactive",
    }

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "coupon_code", "discount", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"[Logger] Deal logged: {row}")
