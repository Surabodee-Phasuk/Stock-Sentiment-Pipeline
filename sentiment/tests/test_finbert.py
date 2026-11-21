import pytest

from sentiment.finbert import (
    LABELS,
    MAX_SUMMARY_CHARS,
    MODEL_NAME,
    MODEL_VERSION,
    FinBertClassifier,
    build_text,
    to_prediction,
)


def fake_probs(texts):
    """โมเดลปลอม: คำว่า beat = บวก, miss = ลบ นอกนั้นกลาง."""
    out = []
    for t in texts:
        if "beat" in t:
            out.append({"positive": 0.9, "neutral": 0.08, "negative": 0.02})
        elif "miss" in t:
            out.append({"positive": 0.05, "neutral": 0.15, "negative": 0.8})
        else:
            out.append({"positive": 0.1, "neutral": 0.8, "negative": 0.1})
    return out


def test_build_text_joins_headline_and_summary():
    assert build_text("Apple beats", "Revenue up 8%") == "Apple beats. Revenue up 8%"
    assert build_text("Done!", "More text") == "Done! More text"


def test_build_text_skips_empty_or_duplicate_summary_and_squeezes_spaces():
    assert build_text("  Apple   beats  ", None) == "Apple beats"
    assert build_text("Apple beats", "apple BEATS") == "Apple beats"
    assert build_text(None, None) == ""


def test_build_text_truncates_long_summary():
    text = build_text("H", "x" * (MAX_SUMMARY_CHARS + 100))
    assert text == "H. " + "x" * MAX_SUMMARY_CHARS


def test_to_prediction_picks_argmax_and_signed_score():
    p = to_prediction({"positive": 0.2, "neutral": 0.1, "negative": 0.7})

    assert p.sentiment == "negative"
    assert p.score == pytest.approx(-0.5)
    assert set(p.probs) == set(LABELS)


def test_to_prediction_requires_all_three_labels():
    with pytest.raises(ValueError):
        to_prediction({"positive": 0.5, "negative": 0.5})


def test_predict_batches_and_keeps_order():
    calls = []

    def spy(texts):
        calls.append(len(texts))
        return fake_probs(texts)

    clf = FinBertClassifier(batch_size=2, prob_fn=spy)
    preds = clf.predict(["NVDA beat", "neutral news", "TSLA miss", "AAPL beat", "x"])

    assert [p.sentiment for p in preds] == [
        "positive",
        "neutral",
        "negative",
        "positive",
        "neutral",
    ]
    assert calls == [2, 2, 1]


def test_predict_empty_input_does_not_load_model():
    clf = FinBertClassifier()  # ไม่มี prob_fn ถ้าโหลดโมเดลจริงจะต้องมี torch

    assert clf.predict([]) == []


def test_predict_detects_wrong_result_count():
    clf = FinBertClassifier(prob_fn=lambda texts: fake_probs(texts)[:-1])

    with pytest.raises(RuntimeError):
        clf.predict(["a", "b"])


def test_defaults_record_model_name_and_version():
    clf = FinBertClassifier()

    assert clf.model_name == MODEL_NAME == "ProsusAI/finbert"
    assert clf.model_version == MODEL_VERSION


def test_rejects_bad_batch_size():
    with pytest.raises(ValueError):
        FinBertClassifier(batch_size=0)
