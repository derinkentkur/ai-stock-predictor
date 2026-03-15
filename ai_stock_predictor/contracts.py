"""Discrete output contract enforcement for model scores."""

from typing import Iterable, List

ALLOWED_SCORES = (0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.00)

ACTION_BY_SCORE = {
    0.35: "Invest",
    0.30: "Divest",
    0.25: "Buy shares",
    0.20: "Sell shares",
    0.15: "Convert currency",
    0.10: "Explore new/random site",
    0.05: "Analyze similar site",
    0.00: "Wait / No action",
}


def normalize_score(raw_score: float) -> float:
    """Clamp to the supported range and quantize to the nearest allowed value."""

    bounded = max(0.0, min(0.35, float(raw_score)))
    normalized = min(
        ALLOWED_SCORES,
        key=lambda allowed: (abs(allowed - bounded), -allowed),
    )
    return round(normalized, 2)


def normalize_scores(raw_scores: Iterable[float]) -> List[float]:
    """Normalize a sequence into the discrete action contract."""

    return [normalize_score(score) for score in raw_scores]


def is_allowed_score(score: float) -> bool:
    """Return whether the score is exactly representable by the action contract."""

    return round(float(score), 2) in ACTION_BY_SCORE


def validate_scores(scores: Iterable[float]) -> None:
    """Raise if any score escapes the discrete output contract."""

    invalid = [score for score in scores if not is_allowed_score(score)]
    if invalid:
        raise ValueError("Scores outside discrete contract: %s" % invalid)


def interpret_actions(scores: Iterable[float]) -> List[str]:
    """Map contract scores to user-facing actions."""

    actions = []
    for score in scores:
        rounded = round(float(score), 2)
        actions.append(ACTION_BY_SCORE.get(rounded, "Wait / No action"))
    return actions
