import pytest

from sentiment.eval.evaluate import (
    confusion,
    metrics,
    read_gold,
    throughput,
    to_markdown,
)
from sentiment.eval.sample_goldset import GOLD_FIELDS, stratified_sample, write_csv
from sentiment.finbert import FinBertClassifier
from sentiment.tests.test_finbert import fake_probs


def test_perfect_prediction():
    gold = ["positive", "neutral", "negative"]
    m = metrics(gold, gold)

    assert m["accuracy"] == 1.0 and m["macro_f1"] == 1.0


def test_metrics_match_hand_calculation():
    gold = ["positive", "positive", "neutral", "neutral", "negative", "negative"]
    pred = ["positive", "neutral", "neutral", "neutral", "positive", "negative"]
    m = metrics(gold, pred)

    # positive: tp1 fp1 fn1 → P=R=F1=0.5 ; neutral: tp2 fp1 fn0 → P=2/3 R=1 F1=0.8
    # negative: tp1 fp0 fn1 → P=1 R=0.5 F1=2/3
    assert m["accuracy"] == pytest.approx(4 / 6)
    assert m["per_label"]["positive"]["f1"] == pytest.approx(0.5)
    assert m["per_label"]["neutral"]["precision"] == pytest.approx(2 / 3)
    assert m["per_label"]["neutral"]["f1"] == pytest.approx(0.8)
    assert m["per_label"]["negative"]["recall"] == pytest.approx(0.5)
    assert m["macro_f1"] == pytest.approx((0.5 + 0.8 + 2 / 3) / 3)
    assert confusion(gold, pred)["negative"]["positive"] == 1


def test_metrics_with_missing_class_has_zero_f1_not_error():
    m = metrics(["positive", "positive"], ["positive", "neutral"])

    assert m["per_label"]["negative"]["f1"] == 0.0
    assert m["per_label"]["negative"]["support"] == 0


def test_stratified_sample_spreads_tickers_and_skips_duplicate_news():
    rows = [
        {"news_id": f"a{i}", "ticker": "AAPL", "headline": f"A{i}"} for i in range(10)
    ]
    rows += [{"news_id": "x", "ticker": "RKLB", "headline": "R"}]
    rows += [{"news_id": "x", "ticker": "SPCX", "headline": "R"}]  # ข่าวเดียวสองหุ้น
    rows += [{"news_id": "e", "ticker": "NVDA", "headline": " "}]  # headline ว่าง

    picked = stratified_sample(rows, 4, seed=1)

    assert len(picked) == 4
    assert [r["news_id"] for r in picked].count("x") == 1
    assert {r["ticker"] for r in picked} >= {"AAPL", "RKLB"}
    assert all(r["news_id"] != "e" for r in picked)
    assert stratified_sample(rows, 4, seed=1) == picked  # seed เดิมได้ชุดเดิม


def test_gold_csv_roundtrip_and_label_validation(tmp_path):
    out = tmp_path / "gold.csv"
    write_csv([{"news_id": "n1", "ticker": "AAPL", "headline": "Apple beat"}], out)
    header = out.read_text("utf-8").splitlines()[0].split(",")
    assert tuple(header) == GOLD_FIELDS

    with pytest.raises(ValueError):
        read_gold(out)  # label ยังว่าง

    out.write_text(out.read_text("utf-8").replace(",,\n", ",Positive,\n"), "utf-8")
    assert read_gold(out)[0]["label"] == "positive"


def test_throughput_and_markdown_with_fake_model():
    clf = FinBertClassifier(prob_fn=fake_probs, batch_size=4)
    t = throughput(clf, ["a beat", "b miss", "c"] * 4, repeats=2)

    assert t["texts"] == 12 and t["news_per_second"] > 0
    md = to_markdown(
        "poc",
        {
            "model_name": "m",
            "model_version": "v",
            "machine": "test",
            "run_at": "now",
            "metrics": metrics(["positive"], ["positive"]),
            "throughput": t,
        },
    )
    assert "Macro-F1" in md and "ข่าว/วินาที" in md
