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

https://github.com/bdragon42/financial-reporting/blob/master/finance_streaming_architecture.drawio.png

## Data Flow Diagram

![Kafka Streaming Architecture](https://raw.githubusercontent.com/bdragon42/financial-reporting/master/finance_streaming_architecture.drawio%20(1).png)

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

