"""One-off script for Problem 11: drives the live site with Playwright (system
Chrome) to capture real, working-app screenshots for output/app_check.html.
Not part of the app itself -- a verification tool.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
IMAGES_DIR = HERE / "app_check_images"
IMAGES_DIR.mkdir(exist_ok=True)
BASE_URL = "http://localhost:5176"


def wait_for_reply(page, expected_min_bubbles):
    page.wait_for_function(
        """(min) => {
            const bubbles = document.querySelectorAll('.chat-bubble');
            if (bubbles.length < min) return false;
            const last = bubbles[bubbles.length - 1];
            return !last.textContent.includes('Thinking');
        }""",
        arg=expected_min_bubbles,
        timeout=30000,
    )


def send_chat_message(page, message):
    page.fill(".chat-widget__input-row input", message)
    page.click(".chat-widget__input-row button[type=submit]")


def scroll_chat_to_bottom(page):
    page.evaluate(
        """() => {
            const el = document.querySelector('.chat-widget__messages');
            if (el) el.scrollTop = el.scrollHeight;
        }"""
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # --- Check 1: chat inventory/stock + price pull from the db ---
        page.goto(f"{BASE_URL}/products/champion-full-zip-hood", wait_until="networkidle")
        page.click(".chat-widget__toggle")
        page.wait_for_selector(".chat-widget__panel")
        send_chat_message(page, "Use the smarter model: how many Champion Full Zip Hoods do you have left in size Large, and what do they cost?")
        wait_for_reply(page, 2)
        page.wait_for_timeout(300)
        scroll_chat_to_bottom(page)
        page.wait_for_timeout(150)
        page.locator(".chat-widget__panel").screenshot(path=str(IMAGES_DIR / "01_chat_stock_check.png"))
        print("Saved 01_chat_stock_check.png")

        # --- Check 2: dynamic search-result cards after a category question ---
        send_chat_message(page, "Show me some hoodies")
        wait_for_reply(page, 4)
        page.wait_for_timeout(300)
        page.click(".chat-widget__toggle")  # close the panel so the page-level cards are unobstructed
        # The results panel is intentionally hidden on product-detail pages (Problem 7
        # design) -- navigate to Home via an in-app link (not page.goto, which would do
        # a hard reload and wipe the in-memory ChatResultsContext) to actually see it.
        page.click('a[href="/"]')
        page.wait_for_selector(".chat-results-panel")
        page.wait_for_timeout(300)
        page.screenshot(path=str(IMAGES_DIR / "02_dynamic_search_cards.png"))
        print("Saved 02_dynamic_search_cards.png")

        # --- Check 3: Problem 9 usability feature - product search/filter bar ---
        page.goto(f"{BASE_URL}/products", wait_until="networkidle")
        page.wait_for_selector(".products-filter-bar")
        page.fill(".products-filter-bar__search", "navy")
        page.wait_for_timeout(300)
        page.screenshot(path=str(IMAGES_DIR / "03_usability_filter_bar.png"))
        print("Saved 03_usability_filter_bar.png")

        browser.close()


if __name__ == "__main__":
    main()
