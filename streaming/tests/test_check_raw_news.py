from streaming.check_raw_news import (
    NewsRow,
    describe,
    find_rounds,
    fresh_news,
    percentile,
)

MIN = 60
HOUR = 3600


def _row(news_id, ingested, published=0, loaded=None, ticker="AAPL"):
    return NewsRow(news_id, ticker, published, ingested, loaded or ingested + MIN)


def test_find_rounds_groups_requests_of_the_same_cycle():
    assert find_rounds([0, 30, 45, 5 * MIN, 5 * MIN + 20, 10 * MIN]) == [
        (0, 45),
        (5 * MIN, 5 * MIN + 20),
        (10 * MIN, 10 * MIN),
    ]


def test_first_round_backlog_is_not_fresh():
    rows = [_row("old1", 0), _row("old2", 10), _row("new", 5 * MIN)]

    assert [r.news_id for r in fresh_news(rows)] == ["new"]


def test_restarted_collector_resend_is_not_fresh():
    # เปิด collector ใหม่หลังผ่านไป 3 ชั่วโมง: ส่งข่าวเก่าซ้ำ และมีข่าวที่ออกระหว่างหยุด
    rows = [
        _row("old", 0),
        _row("old", 3 * HOUR),
        _row("during_gap", 3 * HOUR),
        _row("new", 3 * HOUR + 5 * MIN),
    ]

    assert [r.news_id for r in fresh_news(rows)] == ["new"]


def test_same_news_counts_separately_per_ticker():
    rows = [
        _row("first", 0),
        _row("n", 5 * MIN, ticker="AAPL"),
        _row("n", 5 * MIN, ticker="MSFT"),
    ]

    assert {(r.news_id, r.ticker) for r in fresh_news(rows)} == {
        ("n", "AAPL"),
        ("n", "MSFT"),
    }


def test_news_uses_its_first_seen_row():
    rows = [
        _row("first", 0),
        _row("n", 5 * MIN, loaded=6 * MIN),
        _row("n", 10 * MIN, loaded=11 * MIN),
    ]

    assert [r.loaded_at for r in fresh_news(rows)] == [6 * MIN]


def test_describe_counts_within_15_minutes():
    assert percentile([1, 2, 3, 4], 0.5) == 3
    assert describe([60, 900, 901]) == ("p50=900s p95=901s max=901s within_15min=2/3")
