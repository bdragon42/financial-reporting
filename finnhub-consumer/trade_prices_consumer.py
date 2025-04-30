from confluent_kafka import Consumer
import json
import time
import statistics
import boto3
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = 'finance-streaming-data'

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'finance-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['finance-streaming'])

print("Subscribed to topic")

windows = {}
start_time = time.time()

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error:", msg.error())
            continue

        try:
            value = json.loads(msg.value().decode('utf-8'))
            if value.get("type") != "trade":
                continue

            for trade in value.get("data", []):
                symbol = trade["s"]
                if symbol not in windows:
                    windows[symbol] = []
                windows[symbol].append(trade)

        except Exception as e:
            print("Failed to parse message:", e)

        if time.time() - start_time >= 60:
            for symbol, trades in windows.items():
                prices = [t["p"] for t in trades if t.get("p")]
                volumes = [t["v"] for t in trades if t.get("p") and t.get("v")]

                if prices and volumes:
                    vwap = sum(p * v for p, v in zip(prices, volumes)) / sum(volumes)
                    rate = len(trades) / 60
                    delta = prices[-1] - prices[0]
                    volatility = statistics.stdev(prices) if len(prices) > 1 else 0

                now = datetime.utcnow()
                path = f"trades/{symbol}/{now.year}/{now.month:02}/{now.day:02}.jsonl"
                data_jsonl = '\n'.join(json.dumps(t) for t in trades)
                s3.put_object(Bucket=bucket_name, Key=path, Body=data_jsonl.encode('utf-8'))

            windows = {}
            start_time = time.time()

except KeyboardInterrupt:
    print("Exiting...")
finally:
    consumer.close()