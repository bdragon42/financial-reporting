import requests
import pandas as pd
from datetime import datetime
import finnhub
import boto3
import os
import json

s3 = boto3.client('s3')
FINNHUB_API_KEY = "cvm7u61r01qnndmcnj9gcvm7u61r01qnndmcnja0"  # Replace with your actual API key
TRACKER_KEY = "date-tracker/filing_tracker.json"

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

symbol_cache = []
last_updated = None



def load_filing_tracker(bucket):
    try:
        response = s3.get_object(Bucket=bucket, Key=TRACKER_KEY)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except s3.exceptions.NoSuchKey:
        print("No existing tracker file — starting fresh.")
        return {}
    except Exception as e:
        print(f"Error loading tracker from S3: {e}")
        return {}

def save_filing_tracker(tracker, bucket):
    s3.put_object(
        Bucket=bucket,
        Key=TRACKER_KEY,
        Body=json.dumps(tracker, indent=2).encode('utf-8'),
        ContentType='application/json'
    )
    print(f"Saved tracker to s3://{bucket}/{TRACKER_KEY}")

def upload_filings(json_data, symbol, bucket, prefix):
    key = f"{prefix}{symbol}_{datetime.utcnow().isoformat()}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json_data.encode('utf-8'),
        ContentType='application/json'
    )
    print(f"Uploaded {symbol} data to s3://{bucket}/{key}")

def should_refresh_symbols():
    global last_updated
    now = datetime.utcnow()
    if last_updated is None or now.month != last_updated.month or now.year != last_updated.year:
        last_updated = now
        return True
    return False

def get_symbols():
    global symbol_cache
    if not should_refresh_symbols():
        return symbol_cache

    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    nasdaq_symbols = finnhub_client.stock_symbols('US')  # 'US' gives both NASDAQ and NYSE
    df = pd.DataFrame(nasdaq_symbols)

    # Filter to only Common Stocks listed on NYSE/NASDAQ
    filtered_df = df[
        (df['type'] == 'Common Stock') &
        (df['mic'].isin(['XNYS', 'XNAS'])) &
        (df['currency'] == 'USD')
        ]

    filtered_symbols = filtered_df['symbol'].tolist()[:10]

    return filtered_symbols
def get_financials_reported(symbol, limit=1, s3_bucket=None, tracker=None):
    url = "https://finnhub.io/api/v1/stock/financials-reported"
    params = {
        'symbol': symbol,
        'token': FINNHUB_API_KEY,
        'limit': limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching{symbol}: {e}")
        return

    if not data or not isinstance(data, dict):
        print(f"Malformed response for {symbol}")
        return

    reports = data.get("data", [])

    df = pd.json_normalize(reports)
    print(df.columns.tolist())

    if not reports:
        print(f"No financial data found for {symbol}")
        return

    latest_saved = tracker.get(symbol)
    new_reports = [r for r in reports if r.get('filedDate', '') > (latest_saved or "")]

    if not new_reports:
        print(f"No new reports for {symbol}")
        return

    if s3_bucket:
        flat_rows = []
        for report in new_reports:
            filed_date = report.get("filedDate")
            form = report.get("form")
            section = report.get("report", {})

            for stmt_type in ["bs", "ic", "cf"]:
                for item in section.get(stmt_type, []):
                    flat_rows.append({
                        "symbol": symbol,
                        "filedDate": filed_date,
                        "form": form,
                        "statement": stmt_type,
                        "concept": item.get("concept"),
                        "label": item.get("label"),
                        "value": item.get("value"),
                        "unit": item.get("unit")
                    })

        json_lines = "\n".join(json.dumps(row) for row in flat_rows)
        upload_filings(json_lines, symbol, s3_bucket, filing_folder)

    latest_filed = max([r['filedDate'] for r in new_reports])
    tracker[symbol] = latest_filed

# Example usage
if __name__ == "__main__":
    s3_bucket = "reported-financials"
    date_tracker_folder = "date-tracker/"
    filing_folder = "filings/"
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

    tracker = load_filing_tracker(s3_bucket)

    for symbol in symbols:
        try:
            get_financials_reported(
                symbol,
                limit=10,
                s3_bucket=s3_bucket,
                tracker=tracker
            )
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    save_filing_tracker(bucket=s3_bucket, tracker=tracker)

