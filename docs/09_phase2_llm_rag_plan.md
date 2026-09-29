# Phase 2 Plan — Agentic AI with LLM (LLM Summary + News RAG)

Timeline: January – April

Phase 2 adds Agentic AI on top of the Phase 1 data (news + FinBERT sentiment + daily price).
It has two parts: **LLM Summary** and **News RAG**.

## 1. LLM Summary (Stock Detail page)

- Summarizes each stock's news of the day.
- Explains why the overall news sentiment is Positive / Neutral / Negative.
- Output is a medium-length reason summary (not too short, not too long), e.g. 3–5 sentences.
- Input is only news already stored in the Lakehouse for that ticker, plus its FinBERT labels.
- Shown on the **Stock Detail page** of each stock, next to the overall sentiment card.

## 2. News RAG (Q&A)

- Users ask questions about news of stocks, e.g. "Why is TSLA news negative this week?"
- Retrieval is filtered to the ticker in the question; answers cite source news (headline, source, time).
- Answers only for stocks in the project's stock list (~50). Out-of-scope questions
  (other tickers, buy/sell advice, unrelated topics) are refused.
- Added as an **"Ask AI" tab in the bottom menu bar** (Home · Search · Ask AI · Profile),
  covering every stock in the project list.

## Evaluation

| Part | Test set | Metrics | Baseline |
|---|---|---|---|
| LLM Summary | Randomly sample ~50 summaries | Content matches the real news; no hallucinated facts; overall Positive/Neutral/Negative agrees with FinBERT | Different prompts / models |
| News RAG | ~50–100 test questions (in-scope + out-of-scope) | Retrieves news of the correct ticker; answer grounded in real news with citations; correctly refuses out-of-scope questions; latency and cost | LLM without RAG |

Comparing against an LLM without RAG shows whether retrieval actually improves answer accuracy.

## Notes

- Sentiment and AI answers are informational only, not investment advice.
- Candidate stack: Amazon Bedrock (LLM + embeddings), a vector store over ingested news.
