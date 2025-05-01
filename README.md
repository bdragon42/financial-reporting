# 📈 Real-Time Stock Data Pipeline

This project is a real-time streaming and financial data ingestion pipeline built to process both **trade data** and **financial report filings** for a curated set of stock symbols. It utilizes **Kafka**, **AWS**, **Kubernetes**, and **Glue + Redshift Spectrum** to produce a scalable data platform for downstream analytics and potential trading research.

---

## ⚙️ Architecture Overview

### 🧩 Components

| Component | Description |
|----------|-------------|
| `producer` | Connects to Finnhub WebSocket API and streams trade data |
| `consumer` | Consumes trade data from Kafka and writes JSONL to S3 |
| `filing_collector` | Periodically fetches SEC/financial reports via Finnhub REST API |
| AWS Glue Crawlers | Crawl S3 folders (trades + filings), update Glue Catalog schemas |
| Redshift Spectrum | Queries external tables directly from S3 via Glue |
| K3s | lightweight version of kubernetes to be ran on a single EC2 instance |

---

## 🔄 Data Flow Summary

1. **Trade Producer** connects to Finnhub WebSocket and streams live trade events into Kafka topics.
2. **Trade Consumer** reads from Kafka and writes per-symbol trade data to S3 in `.jsonl` format (partitioned by date and symbol).
3. **Filing Collector** periodically pulls financial statement submissions via REST API and stores those in a separate S3 folder.
4. Two AWS Glue Crawlers index both S3 locations and create separate databases (`trades_db`, `filings_db`) in the AWS Glue Data Catalog.
5. Redshift Spectrum queries the Glue databases via external schemas.

*The Finnhub API key used is the one provided by Finnhub for all free user accounts.*

---

## 🔎 Sample Metrics Calculated

From trade data:
- **VWAP** – Volume-Weighted Average Price
- **Volatility** – Rolling standard deviation of trade prices
- **Trade Rate** – Number of trades per second

From financial filings:
- Document metadata such as **form type**, **filing date**, and **fiscal period end**
- Full JSON content of earnings reports, 10-Ks, 10-Qs

---

## 🧭 Roadmap

- [x] Kafka producer & consumer containers  
- [x] Filing data ingestion pipeline  
- [x] JSONL export to S3 (partitioned)  
- [x] AWS Glue Crawlers for schema discovery  
- [x] External schema access via Redshift Spectrum  
- [ ] Backtest module for strategies  
- [ ] Streamlit/Looker Studio dashboard  
- [ ] Trading signal prototype

