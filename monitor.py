from playwright.sync_api import sync_playwright
import os
import json
import requests
from datetime import datetime


URL = "https://www.nikonusa.com/p/z-30-refurbished/1749Q"

PRICE_FILE = "price.json"


def get_price():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        # Get all visible text
        text = page.locator("body").inner_text()

        browser.close()


    print(text[:3000])


    import re


    # Look for Z30 + 16-50mm lens kit price
    pattern = r'Z\s*30.*?16-50mm.*?\$([0-9,]+\.\d{2})'

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        price = match.group(1)

        return float(
            price.replace(",", "")
        )


    # Backup method if text order changes
    print("Specific kit not found, checking prices...")


    prices = re.findall(
        r'\$[0-9,]+\.\d{2}',
        text
    )


    print("FOUND PRICES:", prices)


    valid_prices = [
        float(
            x.replace("$","").replace(",","")
        )
        for x in prices
        if float(
            x.replace("$","").replace(",","")
        ) > 200
    ]


    if len(valid_prices) >= 2:
        return valid_prices[1]


    raise Exception(
        "Could not find Nikon Z30 lens kit price"
    )



def send_telegram(old_price, new_price):

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    message = f"""
🚨 Nikon Z30 Price Drop!

Old: ${old_price:.2f}
New: ${new_price:.2f}

Dropped: ${old_price-new_price:.2f}

{URL}
"""

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message
        }
    )


def load_previous_price():

    if not os.path.exists(PRICE_FILE):
        return None

    with open(PRICE_FILE) as f:
        return json.load(f)["price"]



def save_price(price):

    with open(PRICE_FILE, "w") as f:
        json.dump(
            {
                "price": price,
                "time": str(datetime.now())
            },
            f,
            indent=4
        )



def main():

    current = get_price()

    previous = load_previous_price()

    print("Current:", current)
    print("Previous:", previous)


    if previous and current < previous:

        send_telegram(
            previous,
            current
        )

        print("Alert sent!")

    else:
        print("No drop.")


    save_price(current)



if __name__ == "__main__":
    main()
