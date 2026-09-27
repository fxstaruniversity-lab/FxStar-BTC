import os
import time
import requests
from datetime import datetime, timezone

BINANCE_URL = "https://api.binance.com/api/v3/klines"
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOL = os.getenv("BTC_SYMBOL", "BTCUSDT")
INTERVAL = "1h"
LOOKBACK = int(os.getenv("LOOKBACK", "20"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))

last_closed_candle = None
last_alert_key = None


def get_klines(limit=LOOKBACK + 5):
    r = requests.get(
        BINANCE_URL,
        params={"symbol": SYMBOL, "interval": INTERVAL, "limit": limit},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def send_telegram(message):
    url = TELEGRAM_URL.format(BOT_TOKEN)
    r = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": message},
        timeout=15,
    )
    r.raise_for_status()


def analyze():
    global last_closed_candle, last_alert_key

    candles = get_klines()

    # The last candle is normally still forming. Use the latest fully closed candle.
    closed = candles[:-1]
    current = closed[-1]
    candle_time = int(current[0])

    if candle_time == last_closed_candle:
        return
    last_closed_candle = candle_time

    close = float(current[4])
    high = float(current[2])
    low = float(current[3])

    prior = closed[-LOOKBACK-1:-1]
    prior_high = max(float(c[2]) for c in prior)
    prior_low = min(float(c[3]) for c in prior)

    event = None

    if close > prior_high:
        event = "BREAKOUT_UP"
    elif close < prior_low:
        event = "BREAKDOWN"

    if not event:
        return

    alert_key = f"{event}:{candle_time}"
    if alert_key == last_alert_key:
        return
    last_alert_key = alert_key

    utc = datetime.fromtimestamp(candle_time / 1000, tz=timezone.utc)
    direction = "BULLISH BREAKOUT" if event == "BREAKOUT_UP" else "BEARISH BREAKDOWN"

    message = (
        f"🚨 FXSTAR BTCUSD ALERT\n\n"
        f"₿ BTCUSDT: ${close:,.0f}\n\n"
        f"EVENT: {direction}\n"
        f"TIMEFRAME: 1H\n\n"
        f"KEY LEVEL\n"
        f"Previous {LOOKBACK}H high: ${prior_high:,.0f}\n"
        f"Previous {LOOKBACK}H low: ${prior_low:,.0f}\n\n"
        f"1H candle high: ${high:,.0f}\n"
        f"1H candle low: ${low:,.0f}\n\n"
        f"⚠️ TECHNICAL ANALYSIS ONLY\n"
        f"NO INVESTMENT ADVICE\n\n"
        f"Closed: {utc.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    send_telegram(message)
    print(message, flush=True)


def main():
    print("FxStar BTCUSD alert agent started.", flush=True)
    while True:
        try:
            analyze()
        except Exception as exc:
            print(f"ERROR: {exc}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
