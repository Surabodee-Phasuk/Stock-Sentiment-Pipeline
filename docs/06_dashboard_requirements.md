# Dashboard Data Requirements

## Page 1 — Stock Selection
Needs:
- ticker
- company name
- sector
- search/filter
- selected count

## Page 2 — Watchlist
Primary focus: sentiment, not technical trading indicators.
Each card should be able to show:
- ticker / company name
- current price
- price change %
- sentiment badge
- positive / neutral / negative percentages
- compact sparkline (optional/contextual)
- last updated

## Page 3 — Stock Detail Dashboard
Needs:
- current price and change
- sentiment distribution
- Price vs News Sentiment chart
- latest news list
- source and sentiment score per news item
- basic system health

## UX principle
The main user question is: “ข่าวของหุ้นนี้ช่วงล่าสุดมีทิศทางเป็นบวก กลาง หรือลบ?” The UI should answer that quickly.

## Important boundary
Sentiment is not a price prediction and must not be presented as a buy/sell recommendation.
