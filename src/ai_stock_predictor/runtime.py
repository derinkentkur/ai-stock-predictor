"""Multi-model runtime, candidate generation, and autonomous promotion."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import random
from typing import Any

from .actions import interpret_score
from .dashboard import build_dashboard
from .ingestion import InputBundle
from .logging_store import append_jsonl
from .models import ModelSpec, baseline_model, mutate_model
from .portfolio import PortfolioState, apply_action


PREDICTION_LOG = "logs/predictions.jsonl"
PROMOTION_LOG = "logs/promotions.jsonl"
DASHBOARD_HTML = "dashboards/index.html"


def evaluate_model(model: ModelSpec, bundle: InputBundle, outputs: int, initial_cash: float) -> dict[str, Any]:
    state = PortfolioState(cash=initial_cash)
    features = bundle.features()
    raw = model.predict(features, outputs=outputs)
    interpreted = [interpret_score(v) for v in raw]
    for out in interpreted:
        apply_action(out.action, state, price=bundle.market_prices[-1])

    portfolio_value = state.value(bundle.market_prices[-1])
    pnl = portfolio_value - initial_cash
    return {
        "model_version": model.version,
        "model": asdict(model),
        "raw_outputs": raw,
        "normalized_outputs": [o.score for o in interpreted],
        "actions": [o.action for o in interpreted],
        "portfolio_state": asdict(state),
        "portfolio_value": portfolio_value,
        "profit_loss": pnl,
        "features": features,
    }


def run_cycle(bundle: InputBundle, n_alternatives: int = 3, outputs_per_model: int = 4,
              seed: int = 123, initial_cash: float = 10_000.0) -> dict[str, Any]:
    rng = random.Random(seed)
    primary = baseline_model(seed=seed)
    candidates = [primary] + [mutate_model(primary, i + 1, rng) for i in range(n_alternatives)]

    evaluations = [evaluate_model(m, bundle, outputs_per_model, initial_cash) for m in candidates]
    winner = max(evaluations, key=lambda e: (e["profit_loss"], e["portfolio_value"]))

    timestamp = datetime.now(timezone.utc).isoformat()
    for evaluation in evaluations:
        append_jsonl(
            PREDICTION_LOG,
            {
                "timestamp": timestamp,
                "inputs": {
                    "webpage_bytes": len(bundle.webpage_bytes),
                    "market_prices": bundle.market_prices,
                    "financial_api_signal": bundle.financial_api_signal,
                    "news_sentiment": bundle.news_sentiment,
                    "economic_indicator": bundle.economic_indicator,
                },
                **evaluation,
            },
        )

    if winner["model_version"] != primary.version:
        append_jsonl(
            PROMOTION_LOG,
            {
                "timestamp": timestamp,
                "previous_primary": primary.version,
                "new_primary": winner["model_version"],
                "reason": "higher profit or reduced loss",
            },
        )

    build_dashboard(PREDICTION_LOG, DASHBOARD_HTML)
    return {"timestamp": timestamp, "winner": winner, "evaluations": evaluations}
