# AI Investor Research Platform

An automated AI-powered investor intelligence platform that collects financial news, analyzes sentiment, enriches reports with market data, and generates personalized daily investor briefs.

## Overview

This project was built as a portfolio project focused on:
- financial data engineering,
- SQL-based data architecture,
- NLP / sentiment analysis,
- automated reporting pipelines,
- investor intelligence systems.

The platform automatically:
1. Collects market news for portfolio holdings,
2. Filters relevant articles using a custom relevance engine,
3. Performs sentiment analysis,
4. Enriches reports with market data,
5. Generates portfolio analytics,
6. Sends automated investor briefs via email.

---

# Features

## Automated News Pipeline
- Financial news ingestion
- Relevance filtering engine
- Duplicate protection
- Scheduled execution via Windows Task Scheduler

## NLP / AI Layer
- Sentiment analysis
- TF-IDF relevance scoring
- Alias-based company matching
- Keyword extraction
- Portfolio-level sentiment analytics

## Market Intelligence
- Latest market prices
- OHLC session data
- Volume tracking
- Daily move calculations
- Sector exposure analytics

## Personalized Investor Briefs
- Portfolio-specific reporting
- Executive summaries
- Sector overview
- Alerts system
- HTML email delivery

---

# Tech Stack

## Backend
- Python
- SQL Server
- pyodbc
- pandas

## NLP / AI
- scikit-learn
- Hugging Face Transformers
- TF-IDF similarity
- Sentiment classification

## Automation
- Windows Task Scheduler
- Logging system
- Automated ETL pipeline

---

# Database Architecture

Core tables:
- Investors
- Portfolios
- PortfolioHoldings
- Companies
- CompanyKeywords
- News
- SentimentAnalysis
- MarketData
- DailyBriefs
- EmailDeliveryLog

---

# Example Brief Content

The system generates investor reports containing:

- portfolio analytics,
- market snapshots,
- sector intelligence,
- sentiment analysis,
- alerts,
- relevant company news.

## Example sections

- Executive Summary
- Portfolio Analytics
- Alerts
- Sector Overview
- Company-Level Analysis
- Market Snapshot

---

# Current Development Roadmap

## PHASE 1 — Stabilization

- [x] Logging system
- [x] Scheduler automation
- [x] HTML email delivery
- [x] Duplicate protection
- [x] SQL scripts
- [x] Company import system

---

## PHASE 2 — Intelligence

- [x] Sector news
- [x] Portfolio analytics
- [x] Better relevance engine
- [x] Alerts system

---

## PHASE 3 — AI Layer

- [ ] LLM synthesis
- [ ] Semantic embeddings
- [ ] AI summarization
- [ ] Advanced semantic relevance

---

## PHASE 4 — Productization

- [ ] Cloud deployment
- [ ] Docker support
- [ ] Web dashboard
- [ ] Authentication system
- [ ] API layer

---

# Planned Improvements

Future improvements may include:

- vector embeddings,
- semantic search,
- real-time alerts,
- portfolio performance tracking,
- recommendation engine,
- web application frontend,
- cloud-native deployment.

---

# Purpose

This project was created as a hands-on learning and portfolio project focused on:

- AI engineering,
- financial analytics,
- backend systems,
- SQL architecture,
- automation,
- applied NLP.

---

# Disclaimer

This project is for educational and portfolio purposes only and does not constitute investment advice.



# Project Structure

```text
AIAssetSupport/
│
├── framework/
│   ├── load_news.py
│   ├── load_market_data.py
│   ├── analyze_sentiment.py
│   ├── generate_brief_v3.py
│   ├── send_briefs_v3.py
│   ├── relevance_engine.py
│   ├── import_companies.py
│   ├── import_company_aliases.py
│   └── run_daily_pipeline.py
│
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_seed_investors.sql
│   └── 03_seed_portfolios.sql
│
├── data/
│   ├── companies.csv
│   └── company_aliases.csv
│
├── logs/
│
└── README.md

---
