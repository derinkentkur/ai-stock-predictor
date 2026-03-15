"""Local-first input ingestion for market rows and full webpage binaries."""

from dataclasses import dataclass
from hashlib import sha256
from math import log2
from pathlib import Path
import csv
from typing import Dict, List, Sequence, Tuple


FEATURE_NAMES = (
    "close_scaled",
    "intraday_return",
    "range_ratio",
    "momentum_3",
    "momentum_5",
    "volume_scaled",
    "page_size_scaled",
    "unique_byte_ratio",
    "html_tag_ratio",
    "alpha_ratio",
    "digit_ratio",
    "entropy_ratio",
    "hash_signal",
)


@dataclass(frozen=True)
class MarketObservation:
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class InputBundle:
    cycle_index: int
    market: MarketObservation
    next_close: float
    webpage_path: str
    webpage_sha256: str
    feature_vector: Tuple[float, ...]
    input_summary: Dict[str, object]


def load_market_data(path: Path) -> List[MarketObservation]:
    """Load structured market rows from local CSV data."""

    observations = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            observations.append(
                MarketObservation(
                    timestamp=row["timestamp"],
                    symbol=row["symbol"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(row["volume"]),
                )
            )
    if len(observations) < 2:
        raise ValueError("At least two market rows are required.")
    return observations


def list_webpages(directory: Path) -> List[Path]:
    """Return the locally available webpages for binary ingestion."""

    webpages = sorted(directory.glob("*.html"))
    if not webpages:
        raise ValueError("No webpage samples found in %s" % directory)
    return webpages


def select_webpage(
    webpages: Sequence[Path],
    cycle_index: int,
    previous_actions: Sequence[str],
    random_seed: int,
) -> Path:
    """Pick the next webpage using the prior cycle's non-trading exploration actions."""

    if not webpages:
        raise ValueError("No webpage candidates available.")

    if "Explore new/random site" in previous_actions:
        index = (cycle_index * 3 + random_seed) % len(webpages)
        return webpages[index]
    if "Analyze similar site" in previous_actions:
        index = (cycle_index + 1) % len(webpages)
        return webpages[index]
    return webpages[cycle_index % len(webpages)]


def build_input_bundle(
    market_rows: Sequence[MarketObservation],
    cycle_index: int,
    webpage_path: Path,
) -> InputBundle:
    """Build a unified feature representation for one prediction cycle."""

    current = market_rows[cycle_index]
    next_observation = market_rows[cycle_index + 1]
    raw_bytes = webpage_path.read_bytes()
    decoded = raw_bytes.decode("utf-8", errors="ignore")
    feature_vector = _build_feature_vector(market_rows, cycle_index, raw_bytes, decoded)
    digest = sha256(raw_bytes).hexdigest()
    input_summary = {
        "market": {
            "timestamp": current.timestamp,
            "symbol": current.symbol,
            "open": current.open,
            "high": current.high,
            "low": current.low,
            "close": current.close,
            "volume": current.volume,
            "next_close": next_observation.close,
        },
        "webpage": {
            "path": str(webpage_path),
            "bytes": len(raw_bytes),
            "sha256": digest,
        },
        "feature_names": list(FEATURE_NAMES),
    }
    return InputBundle(
        cycle_index=cycle_index,
        market=current,
        next_close=next_observation.close,
        webpage_path=str(webpage_path),
        webpage_sha256=digest,
        feature_vector=feature_vector,
        input_summary=input_summary,
    )


def _build_feature_vector(
    market_rows: Sequence[MarketObservation],
    cycle_index: int,
    raw_bytes: bytes,
    decoded: str,
) -> Tuple[float, ...]:
    current = market_rows[cycle_index]
    closes = [row.close for row in market_rows]
    feature_values = (
        round(current.close / 1_000.0, 6),
        round(_safe_ratio(current.close - current.open, current.open), 6),
        round(_safe_ratio(current.high - current.low, current.open), 6),
        round(_momentum(closes, cycle_index, 3), 6),
        round(_momentum(closes, cycle_index, 5), 6),
        round(current.volume / 10_000_000.0, 6),
        round(min(len(raw_bytes) / 20_000.0, 1.0), 6),
        round(len(set(raw_bytes)) / 256.0, 6),
        round(decoded.count("<") / max(len(decoded), 1), 6),
        round(sum(character.isalpha() for character in decoded) / max(len(decoded), 1), 6),
        round(sum(character.isdigit() for character in decoded) / max(len(decoded), 1), 6),
        round(_byte_entropy(raw_bytes) / 8.0, 6),
        round(int(sha256(raw_bytes).hexdigest()[:6], 16) / float(0xFFFFFF), 6),
    )
    return feature_values


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _momentum(closes: Sequence[float], cycle_index: int, window: int) -> float:
    start = max(0, cycle_index - window + 1)
    window_closes = closes[start : cycle_index + 1]
    anchor = window_closes[0]
    current = window_closes[-1]
    return _safe_ratio(current - anchor, anchor)


def _byte_entropy(raw_bytes: bytes) -> float:
    if not raw_bytes:
        return 0.0
    counts = {}
    for value in raw_bytes:
        counts[value] = counts.get(value, 0) + 1
    entropy = 0.0
    total = float(len(raw_bytes))
    for count in counts.values():
        probability = count / total
        entropy -= probability * log2(probability)
    return entropy
