import json
import os
import re

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

URL = "https://www.nikonusa.com/p/z-30-refurbished/1749Q"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PRICE_FILE = "price.json"


def load_last_price():
    if not os.path.exists(PRICE_FILE):
        return None

    with open(PRICE_FILE, "r") as f:
        return json.load(f).get("last_price")


def save_price(price):
    with open(PRICE_FILE, "w") as f:
        json.dump({"last_price": price}, f)


def get_price():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    text = soup.get_text(" ", strip=True)

    prices = re.findall(r"\$ ?(\d+(?:,\d{3})*(?:\.\d{2})?)", text)

    if not prices:
        raise Exception("Price not found.")

    values = [float(p.replace(",", "")) for p in prices]

    # Choose the lowest price shown
    return min(values)


def send_sms(old_price, new_price):
    client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    body = (
        f"🎉 Nikon Z30 Refurbished price dropped!\n\n"
        f"${old_price:.2f} → ${new_price:.2f}\n\n"
        f"{URL}"
    )

    client.messages.create(
        body=body,
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        to=os.environ["YOUR_PHONE_NUMBER"]
    )


def main():
    current = get_price()
    previous = load_last_price()

    print("Current:", current)
    print("Previous:", previous)

    if previous is None:
        save_price(current)
        print("Baseline saved.")
        return

    if current < previous:
        send_sms(previous, current)
        print("SMS sent!")

    save_price(current)


if __name__ == "__main__":
    main()
