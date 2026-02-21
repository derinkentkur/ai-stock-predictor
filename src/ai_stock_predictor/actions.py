"""Discrete output contract for model actions."""

from __future__ import annotations

from dataclasses import dataclass


ALLOWED_SCORES: tuple[float, ...] = (0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.00)

SCORE_TO_ACTION: dict[float, str] = {
    0.35: "invest",
    0.30: "divest",
    0.25: "buy_shares",
    0.20: "sell_shares",
    0.15: "convert_currency",
    0.10: "explore_new_random_site",
    0.05: "analyze_similar_site",
    0.00: "wait",
}


@dataclass(frozen=True)
class NormalizedOutput:
    raw: float
    score: float
    action: str


def normalize_score(raw: float) -> float:
    """Return nearest discrete score, clamped to contract values."""
    return min(ALLOWED_SCORES, key=lambda allowed: abs(allowed - raw))


def interpret_score(raw: float) -> NormalizedOutput:
    score = normalize_score(raw)
    return NormalizedOutput(raw=raw, score=score, action=SCORE_TO_ACTION[score])
