# Real-Time Stock Data Pipeline

This project is a real-time streaming and financial data ingestion pipeline built to process both **trade data** and **financial report filings** for a curated set of stock symbols. 
It utilizes **Kafka**, **AWS**, **Kubernetes**, **MongoDB** and **Glue + Redshift Spectrum** to produce a scalable data platform for downstream analytics and potential trading research.

README's for various portions of the project detailing nuances of what I was going through will be available within the associated folders.

---
### Financial Analysis & Metrics
This section focuses on ingesting and transforming financial data to build meaningful metrics that drive decision-making.

- [x] Filing data ingestion pipeline
  - [x]  VWAP (Volume-Weighted Average Price)
  - [x]  Volatility (rolling standard deviation of trade prices)
  - [x]  Trades Rate (number of trades per second)
- [ ] Build core financial reports:
  - [ ] Income Statement
  - [ ] Balance Sheet
  - [ ] Cash Flow Statement
- [ ] Derive financial KPIs:
  - [ ] Working Capital
  - [ ] Free Cash Flow
  - [ ] Gross / Net Margin
- [ ] Develop advanced metrics:
  - [ ] WACC (Weighted Average Cost of Capital)
  - [ ] Enterprise Value (E/V)
  - [ ] Debt/Equity Ratio
  - [ ] Asset Turnover & Liquidity Ratios

---

### Plotly Visualizations & Dashboards
This section focuses on turning the above analysis into interactive, visual tools for insight.

- [ ] Design reusable Plotly components:
- [ ] Integrate metrics into visualizations
- [ ] Build a single dashboard combining reports + KPIs

---

### Deployment & Public Access
This section covers exposing the dashboard via a web interface.
- [x] JSONL export to S3 (partitioned)  
- [x] AWS Glue Crawlers for schema discovery  
- [x] External schema access via Redshift Spectrum
- [x] Deployment of MongoDB and associated kafka connector plugin
- [ ] Flask/Dash app on EC2
- [ ] Configure domain URL for public access
- [ ] Develop minimal API to allow dynamic ticker selection

---

## Data Architecture:
The diagram below shows a high level overview of the different components currently operational within the pipeline/project.
This diagram will be updated as new items are added. 

![Kafka Streaming Architecture](https://raw.githubusercontent.com/bdragon42/financial-reporting/master/finance_streaming_architecture.drawio%20(1).png)

