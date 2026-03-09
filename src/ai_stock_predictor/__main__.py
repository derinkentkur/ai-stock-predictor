from __future__ import annotations

import argparse
from pathlib import Path

from .ingestion import build_input_bundle
from .runtime import DASHBOARD_HTML, run_cycle


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one AI stock predictor simulation cycle")
    parser.add_argument("--webpage", default="data/sample_page.bin")
    parser.add_argument("--alternatives", type=int, default=3)
    parser.add_argument("--outputs", type=int, default=4)
    args = parser.parse_args()

    webpage = Path(args.webpage)
    if not webpage.exists():
        webpage.parent.mkdir(parents=True, exist_ok=True)
        webpage.write_bytes(b"<html><body>sample market page</body></html>")

    bundle = build_input_bundle(
        webpage_path=webpage,
        market_prices=[101.0, 103.5, 104.2, 105.1],
        financial_api_signal=0.62,
        news_sentiment=0.55,
        economic_indicator=0.48,
    )
    result = run_cycle(bundle, n_alternatives=args.alternatives, outputs_per_model=args.outputs)
    print(f"Winner: {result['winner']['model_version']} | P/L: {result['winner']['profit_loss']:.2f}")
    print(f"Dashboard: {DASHBOARD_HTML}")


if __name__ == "__main__":
    main()
