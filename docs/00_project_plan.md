# ชีพจรหุ้น (Stock Sentiment Pipeline) — Project Plan Before Coding

## 1. Project Goal
สร้าง Real-time Data Pipeline ที่รวบรวมข้อมูลราคาหุ้นและข่าว/โซเชียล แล้ววิเคราะห์ sentiment เป็น Positive / Neutral / Negative จัดเก็บใน Data Lakehouse และนำเสนอผ่าน Web Application ที่เข้าใจง่าย โดยเน้น “news sentiment” มากกว่าการทำ stock-trading/price-prediction application

## 2. Team
- สุรบดี ผาสุข — 6609650707 — Primary: Data Platform / Ingestion / Lakehouse
- รพินทร์ นะราช — 6609650624 — Primary: Processing / Sentiment / Web App

## 3. Phase 1
Period: 15 Sep – 30 Nov
Focus: Data Engineering
Initial stock pool: ~50 stocks across multiple sectors. Future expansion: ~500 / S&P 500 after Phase 1 is stable.

## 4. Core User Flow
1. Stock Selection
2. Watchlist
3. Stock Detail Dashboard

## 5. Core Pipeline
Stock API + News/RSS/X → Kafka → Spark Structured Streaming → Sentiment / Transform → MinIO + Iceberg + Nessie → Query Layer → Web App

## 6. Definition of Done for Phase 1
- End-to-end pipeline works with sample/real data.
- Data is separated into raw / cleaned / aggregated layers.
- Sentiment is visible as Positive / Neutral / Negative.
- Watchlist and detail dashboard load from pipeline output, not hardcoded UI data.
- Basic reliability/data-quality checks exist.
- System documentation and demo flow are complete.
