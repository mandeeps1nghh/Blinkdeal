import asyncio
import sys
import os

# Ensure imports work regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))

from scraper import scrape_deals
from detector import detect_new_deal
from alerter import send_telegram_alert
from logger import log_deal


async def main():
    print("=" * 50)
    print("[BlinkDeal] Starting deal check...")
    print("=" * 50)

    # Step 1: Scrape the Myntra page
    scrape_result = await scrape_deals()

    if scrape_result.get("error"):
        print(f"[BlinkDeal] Scrape failed: {scrape_result['error']}")
        return

    # Step 2: Detect if a new deal appeared
    should_alert, deal_data = detect_new_deal(scrape_result)

    # Step 3: Send alert if new deal detected
    if should_alert:
        send_telegram_alert(deal_data)

    # Step 4: Log the deal (whether active or not)
    log_deal(deal_data)

    print("=" * 50)
    print("[BlinkDeal] Check complete.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
