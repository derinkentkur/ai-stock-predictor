"""Input ingestion layer for binary webpages + structured market signals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InputBundle:
    webpage_bytes: bytes
    market_prices: list[float]
    financial_api_signal: float
    news_sentiment: float
    economic_indicator: float

    def features(self) -> list[float]:
        binary_mean = sum(self.webpage_bytes) / max(len(self.webpage_bytes), 1) / 255.0
        price_delta = (self.market_prices[-1] - self.market_prices[0]) / max(self.market_prices[0], 1e-9)
        return [
            binary_mean,
            price_delta,
            self.financial_api_signal,
            self.news_sentiment,
            self.economic_indicator,
        ]


def load_webpage_binary(path: str | Path) -> bytes:
    return Path(path).read_bytes()


def build_input_bundle(webpage_path: str | Path, market_prices: list[float], financial_api_signal: float,
                       news_sentiment: float, economic_indicator: float) -> InputBundle:
    return InputBundle(
        webpage_bytes=load_webpage_binary(webpage_path),
        market_prices=market_prices,
        financial_api_signal=financial_api_signal,
        news_sentiment=news_sentiment,
        economic_indicator=economic_indicator,
    )
