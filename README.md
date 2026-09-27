# FxStar BTCUSD Alert Agent

First MVP for Railway.

It polls Binance BTCUSDT 1-hour candles and sends a Telegram alert when a
fully closed 1H candle breaks above the previous 20-hour high or below the
previous 20-hour low.

## Railway variables

Set:

- TELEGRAM_BOT_TOKEN = your BotFather token
- TELEGRAM_CHAT_ID = your channel username, e.g. @yourchannel
- BTC_SYMBOL = BTCUSDT (optional)
- LOOKBACK = 20 (optional)
- POLL_SECONDS = 60 (optional)

Do not commit secrets to GitHub.

## Run locally

pip install -r requirements.txt
python main.py
