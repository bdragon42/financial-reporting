import websocket
import json
from confluent_kafka import Producer
from datetime import datetime, timedelta
import os
# import finnhub
# import pandas as pd



### For Local Testing ###
# producer_config = {
#     'bootstrap.servers': 'localhost:9092'
# }


### For Cluster ###
with open("/etc/kafka-auth/username") as f:
    username = f.read().strip()
with open("/etc/kafka-auth/password") as f:
    password = f.read().strip()

producer_config = {
    'bootstrap.servers': 'kafka.default.svc.cluster.local:9092',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': username,
    'sasl.password': password
}

producer = Producer(producer_config)

key = "cvm7u61r01qnndmcnj9gcvm7u61r01qnndmcnja0" # This is the key provided by Finnhub for all free user accounts.

symbol_cache = []
last_updated = None

def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def on_message(ws, message):
    print("Received", message)
    try:
        producer.produce(
            topic="finance-streaming",
            value=message,
            callback=acked
        )
        producer.poll(0)  # Trigger delivery callback
    except BufferError as e:
        print(f"Buffer full, waiting: {e}")
        producer.poll(1)

def should_refresh_symbols():
    global last_updated
    now = datetime.utcnow()
    if last_updated is None or now.month != last_updated.month or now.year != last_updated.year:
        last_updated = now
        return True
    return False

### Created for possible future scaling of pipelines
# def get_symbols():
#     global symbol_cache
#     if not should_refresh_symbols():
#         return symbol_cache
#
#     finnhub_client = finnhub.Client(api_key=key)
#     nasdaq_symbols = finnhub_client.stock_symbols('US')  # 'US' gives both NASDAQ and NYSE
#     df = pd.DataFrame(nasdaq_symbols)
#
#     # Filter to only Common Stocks listed on NYSE/NASDAQ
#     filtered_df = df[
#         (df['type'] == 'Common Stock') &
#         (df['mic'].isin(['XNYS', 'XNAS'])) &
#         (df['currency'] == 'USD')
#         ]
#
#     filtered_symbols = filtered_df['symbol'].tolist()[:50]
#
#     return filtered_symbols


def on_open(ws, symbols):
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Closed connection")


if __name__ == "__main__":
    socket = f"wss://ws.finnhub.io?token={key}"
    # symbols = get_symbols()

    symbols = [
        "AAPL",
        "MSFT",
        "TSLA",
        "AMZN",
        "NVDA",
        "JPM",
        "UNH",
        "XOM",
        "META",
        "GOOG"
    ]

    ws = websocket.WebSocketApp(socket,
        on_open=lambda ws: on_open(ws, symbols),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.run_forever()