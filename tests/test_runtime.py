from pathlib import Path

from ai_stock_predictor.ingestion import build_input_bundle
from ai_stock_predictor.runtime import run_cycle


def test_cycle_writes_append_only_logs(tmp_path: Path, monkeypatch) -> None:
    prediction_log = tmp_path / "predictions.jsonl"
    promotion_log = tmp_path / "promotions.jsonl"
    dashboard = tmp_path / "dashboard.html"
    monkeypatch.setattr("ai_stock_predictor.runtime.PREDICTION_LOG", str(prediction_log))
    monkeypatch.setattr("ai_stock_predictor.runtime.PROMOTION_LOG", str(promotion_log))
    monkeypatch.setattr("ai_stock_predictor.runtime.DASHBOARD_HTML", str(dashboard))

    webpage = tmp_path / "page.bin"
    webpage.write_bytes(b"abc")
    bundle = build_input_bundle(
        webpage_path=webpage,
        market_prices=[100, 101, 102],
        financial_api_signal=0.6,
        news_sentiment=0.4,
        economic_indicator=0.5,
    )

    run_cycle(bundle, n_alternatives=2, outputs_per_model=3)
    first_count = len(prediction_log.read_text().splitlines())
    run_cycle(bundle, n_alternatives=2, outputs_per_model=3)
    second_count = len(prediction_log.read_text().splitlines())

    assert first_count == 3
    assert second_count == 6
    assert dashboard.exists()
