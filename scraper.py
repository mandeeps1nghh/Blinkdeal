import asyncio
import random
import re
from playwright.async_api import async_playwright

TARGET_URL = "https://www.myntra.com/gold-coin?src=bc"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


async def scrape_deals():
    """Scrape the Myntra Gold Coins page for BlinkDeal coupons."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            java_script_enabled=True,
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )

        # Hide webdriver property to avoid bot detection
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = await context.new_page()

        try:
            # Random delay to appear more human
            await asyncio.sleep(random.uniform(2, 5))

            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)

            # Wait for product content to load
            await page.wait_for_timeout(3000)

            # Take debug screenshot
            await page.screenshot(path="debug_screenshot.png", full_page=True)

            # Extract full page text for deal detection
            page_text = await page.inner_text("body")

            # Look for BlinkDeal / coupon related content
            deal_info = extract_deal_info(page_text)

            # Also try to find coupon elements specifically
            coupon_elements = await page.query_selector_all(
                "[class*='coupon'], [class*='Coupon'], [class*='deal'], [class*='Deal'], "
                "[class*='blink'], [class*='Blink'], [class*='offer'], [class*='Offer'], "
                "[class*='discount'], [class*='Discount']"
            )

            coupon_texts = []
            for el in coupon_elements:
                text = await el.inner_text()
                if text.strip():
                    coupon_texts.append(text.strip())

            if coupon_texts:
                deal_info["coupon_elements_text"] = coupon_texts
                # Re-evaluate deal status with coupon element data
                combined = " ".join(coupon_texts).lower()
                if "blinkdeal" in combined or "blink deal" in combined or "blink" in combined:
                    deal_info["deal_active"] = True
                    deal_info["raw_text"] = " | ".join(coupon_texts)

            print(f"[Scraper] Deal active: {deal_info['deal_active']}")
            print(f"[Scraper] Coupon code: {deal_info['coupon_code']}")
            print(f"[Scraper] Discount: {deal_info['discount']}")
            if coupon_texts:
                print(f"[Scraper] Coupon elements found: {len(coupon_texts)}")
                for ct in coupon_texts[:5]:
                    print(f"  - {ct[:100]}")

            return deal_info

        except Exception as e:
            print(f"[Scraper] Error: {e}")
            # Try to take screenshot even on error
            try:
                await page.screenshot(path="debug_screenshot.png")
            except Exception:
                pass
            return {
                "deal_active": False,
                "coupon_code": None,
                "discount": None,
                "raw_text": None,
                "error": str(e),
            }
        finally:
            await browser.close()


def extract_deal_info(page_text):
    """Parse page text to find BlinkDeal coupon information."""
    text_lower = page_text.lower()

    deal_active = False
    coupon_code = None
    discount = None

    # Check for BlinkDeal keywords
    blink_patterns = ["blinkdeal", "blink deal", "blink_deal"]
    for pattern in blink_patterns:
        if pattern in text_lower:
            deal_active = True
            break

    # Extract coupon codes (typically uppercase alphanumeric)
    coupon_matches = re.findall(r'\b([A-Z][A-Z0-9]{4,15})\b', page_text)
    # Filter out common non-coupon words
    skip_words = {"MYNTRA", "GOLD", "COIN", "COINS", "LOGIN", "SIGNUP", "INDIA", "PRICE", "ADDED", "WISHLIST"}
    coupon_matches = [c for c in coupon_matches if c not in skip_words]
    if coupon_matches:
        coupon_code = coupon_matches[0]

    # Extract discount values
    discount_match = re.search(r'(\d+%\s*(?:off|OFF|discount|DISCOUNT))', page_text)
    if not discount_match:
        discount_match = re.search(r'(flat\s*\d+%)', text_lower)
    if not discount_match:
        discount_match = re.search(r'(₹\s*\d+\s*off)', text_lower)
    if discount_match:
        discount = discount_match.group(1).strip()

    return {
        "deal_active": deal_active,
        "coupon_code": coupon_code,
        "discount": discount,
        "raw_text": page_text[:500] if deal_active else None,
    }


# Allow running standalone for testing
if __name__ == "__main__":
    result = asyncio.run(scrape_deals())
    print("\n--- Scrape Result ---")
    for k, v in result.items():
        if k == "raw_text" and v:
            print(f"  {k}: {v[:200]}...")
        else:
            print(f"  {k}: {v}")
