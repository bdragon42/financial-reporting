# Real-Time Stock Data Pipeline

This project is a real-time streaming and financial data ingestion pipeline built to process both **trade data** and **financial report filings** for a curated set of stock symbols. It utilizes **Kafka**, **AWS**, **Kubernetes**, **MongoDB** and **Glue + Redshift Spectrum** to produce a scalable data platform for downstream analytics and potential trading research.

---

## Architecture Overview

### Components

| Component | Description |
|----------|-------------|
| `producer` | Connects to Finnhub WebSocket API and streams trade data |
| `S3 consumer` | Consumes trade data from Kafka and writes JSONL to S3 |
| `kafka sink connector (consumer)` | Consumes trade data from Kafka and writes to MongoDB |
| `MongoDB` | <ul><li>NoSQL database for real-time processing and merging of trade and filing data</li><li>Future: will be used as source for building Plotly graphs in a front-end service</li></ul> | 
| `filing_collector` | Periodically fetches SEC/financial reports via Finnhub REST API as a batch process. |
| AWS Glue Crawlers | Crawl S3 folders (trades + filings), update Glue Catalog schemas |
| Redshift Spectrum | Queries external tables directly from S3 via Glue |
| K3s | lightweight version of kubernetes to be ran on a single EC2 instance |

---

## Data Flow Diagram
  Batch Analytics:
  1. **Trade Producer** connects to Finnhub WebSocket and streams live trade events into Kafka topics.
  2. **Trade Consumer** reads from Kafka and writes per-symbol trade data to S3 in `.jsonl` format (partitioned by date and symbol).
  3. **Kafka Sink** reads from kafka and writes per-symbol trade data to a MongoDB database. 
  4. **Filing Collector** periodically pulls financial statement submissions via REST API and stores those in a separate S3 folder.
  5. Two AWS Glue Crawlers index both S3 locations and create separate databases (`trades_db`, `filings_db`) in the AWS Glue Data Catalog.
  6. Redshift Spectrum queries the Glue databases via external schemas.
  
  *The Finnhub API key used is the one provided by Finnhub for all free user accounts.*

  Streaming Analytics:



---

## Sample Metrics Calculated

From trade data:
- **VWAP** – Volume-Weighted Average Price
- **Volatility** – Rolling standard deviation of trade prices
- **Trade Rate** – Number of trades per second

From financial filings:
- Document metadata such as **form type**, **filing date**, and **fiscal period end**
- Full JSON content of earnings reports, 10-Ks, 10-Qs

---

## Roadmap

- [x] Kafka producer & consumer containers  
- [x] Filing data ingestion pipeline  
- [x] JSONL export to S3 (partitioned)  
- [x] AWS Glue Crawlers for schema discovery  
- [x] External schema access via Redshift Spectrum  
- [ ] Backtest module for strategies  
- [ ] Streamlit/Looker Studio dashboard  
- [ ] Trading signal prototype

