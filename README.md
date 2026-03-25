# BlinkDeal Tracker

Automated deal tracker that monitors the [Myntra Gold Coins](https://www.myntra.com/gold-coin?src=bc) page for the **BlinkDeal** coupon — a time-limited, high-discount offer that appears at irregular intervals. When the deal goes live, you get an instant Telegram alert.

## How It Works

1. **Scraper** — Playwright loads the Myntra Gold Coins page in headless Chrome and extracts coupon/deal data
2. **Detector** — Compares current state against the last known state to detect new deals (avoids duplicate alerts)
3. **Alerter** — Sends a Telegram notification the moment a deal is detected, plus a status update on every check
4. **Logger** — Records every check to `deals.csv` with timestamps for pattern analysis
5. **Scheduler** — GitHub Actions runs the pipeline every 20 minutes automatically

## Project Structure

```
BlinkDeal/
├── scraper.py          # Playwright scraper for Myntra
├── detector.py         # Deal detection logic + state management
├── alerter.py          # Telegram alert & status updates
├── logger.py           # CSV deal logger
├── main.py             # Orchestrator — single entry point
├── state.json          # Last known deal state (auto-generated)
├── deals.csv           # Deal history log (auto-generated)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for secrets
└── .github/
    └── workflows/
        └── check-deal.yml  # GitHub Actions cron workflow
```

## Setup

### Prerequisites

- Python 3.10+
- Google Chrome installed
- A Telegram bot (create one via [@BotFather](https://t.me/BotFather))

### Installation

```bash
git clone https://github.com/mandeeps1nghh/Blinkdeal.git
cd Blinkdeal
pip install -r requirements.txt
```

### Configuration

Copy the example env file and fill in your Telegram credentials:

```bash
cp .env.example .env
```

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**To get your chat ID:** Message your bot on Telegram, then visit:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```
Look for `"chat": {"id": 123456789}` in the response.

### Run Locally

```bash
python main.py
```

### Deploy on GitHub Actions

1. Push the repo to GitHub
2. Go to **Settings → Secrets → Actions** and add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. The workflow runs automatically every 20 minutes
4. You can also trigger it manually from the **Actions** tab

## Telegram Alerts

- **Deal detected:** `🔥 BlinkDeal LIVE on Myntra!` with coupon code, discount, and link
- **Status check:** `✅ BlinkDeal Bot checked — No active deal found. Next check in ~20 minutes.`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Scraping | Python + Playwright (headless Chrome) |
| Detection | State diffing via JSON |
| Alerts | Telegram Bot API |
| Scheduling | GitHub Actions (cron) |
| Logging | CSV |

## License

MIT
