import requests
import os

NTFY_TOPIC = os.environ["NTFY_TOPIC"]  # set this as a GitHub secret
TICKER = "MU"

def get_price(ticker):
    # Stooq free CSV quote endpoint (no auth, no key needed)
    url = f"https://stooq.com/q/l/?s={ticker.lower()}.us&f=sd2t2ohlcv&h&e=csv"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    header = lines[0].split(",")
    values = lines[1].split(",")
    row = dict(zip(header, values))

    price = float(row["Close"])
    open_price = float(row["Open"])
    change = price - open_price
    pct = (change / open_price) * 100 if open_price else 0.0
    return price, change, pct

def send_notification(topic, title, message):
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={"Title": title}
    )

def main():
    try:
        price, change, pct = get_price(TICKER)
        arrow = "\u2191" if change >= 0 else "\u2193"
        title = f"{TICKER}: ${price:.2f} {arrow}"
        message = f"{TICKER} is ${price:.2f} ({change:+.2f}, {pct:+.2f}%)"
        send_notification(NTFY_TOPIC, title, message)
        print(message)
    except Exception as e:
        send_notification(NTFY_TOPIC, f"{TICKER} check failed", str(e))
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
