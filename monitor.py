import requests
from bs4 import BeautifulSoup
import os
import json
import re
from datetime import datetime


URL = "https://www.nikonusa.com/p/z-30-refurbished/1749Q"

PRICE_FILE = "price.json"


# --------------------------
# Get Nikon price
# --------------------------

def get_price():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7)"
            " AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed loading page: {response.status_code}"
        )

    html = response.text

    # Find dollar prices
    prices = re.findall(
        r'\$[0-9,]+\.\d{2}',
        html
    )

    if not prices:
        raise Exception(
            "Could not find price"
        )

    # Convert first price found
    price = prices[0]

    price = (
        price
        .replace("$", "")
        .replace(",", "")
    )
    print(prices)
    return float(price)



# --------------------------
# Telegram
# --------------------------

def send_telegram(old_price, new_price):

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    message = f"""
🚨 Nikon Z30 Price Drop!

Old price: ${old_price:.2f}
New price: ${new_price:.2f}

Dropped: ${old_price-new_price:.2f}

Checked:
{datetime.now()}
    
{URL}
"""

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message
        }
    )



# --------------------------
# Save / Load
# --------------------------

def load_previous_price():

    if not os.path.exists(PRICE_FILE):
        return None

    with open(PRICE_FILE, "r") as f:
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



# --------------------------
# Main
# --------------------------

def main():

    current_price = get_price()

    previous_price = load_previous_price()


    print(
        f"Current: ${current_price}"
    )

    print(
        f"Previous: ${previous_price}"
    )


    if previous_price:

        if current_price < previous_price:

            send_telegram(
                previous_price,
                current_price
            )

            print(
                "Price dropped! Notification sent."
            )

        else:
            print(
                "No drop."
            )


    save_price(current_price)



if __name__ == "__main__":
    main()
