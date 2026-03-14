"""Portfolio evaluation using simplified profitability-first logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PortfolioState:
    cash: float = 10_000.0
    shares: float = 0.0

    def value(self, latest_price: float) -> float:
        return self.cash + (self.shares * latest_price)


def apply_action(action: str, state: PortfolioState, price: float) -> None:
    if action == "invest" or action == "buy_shares":
        amount = min(state.cash * 0.1, state.cash)
        if amount > 0:
            state.cash -= amount
            state.shares += amount / price
    elif action == "divest" or action == "sell_shares":
        to_sell = state.shares * 0.1
        state.shares -= to_sell
        state.cash += to_sell * price
    elif action == "convert_currency":
        state.cash *= 0.999  # friction placeholder
