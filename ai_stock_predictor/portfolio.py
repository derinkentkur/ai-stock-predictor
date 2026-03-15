"""Paper-trading portfolio simulation for local model evaluation."""

from dataclasses import dataclass
from statistics import pstdev
from typing import Dict, List, Sequence, Tuple


@dataclass
class PortfolioState:
    cash: float
    shares: int
    currency_reserve: float
    total_value: float
    cumulative_pnl: float
    last_price: float

    @classmethod
    def from_cash(cls, initial_cash: float, initial_price: float) -> "PortfolioState":
        return cls(
            cash=round(initial_cash, 2),
            shares=0,
            currency_reserve=0.0,
            total_value=round(initial_cash, 2),
            cumulative_pnl=0.0,
            last_price=initial_price,
        )


def apply_actions(
    portfolio: PortfolioState,
    actions: Sequence[str],
    current_price: float,
    next_price: float,
) -> Tuple[PortfolioState, List[Dict[str, object]], float]:
    """Apply actions in a simulated portfolio with no live brokerage integration."""

    start_value = portfolio.cash + (portfolio.shares * current_price) + portfolio.currency_reserve
    cash = portfolio.cash
    shares = portfolio.shares
    reserve = portfolio.currency_reserve
    activity = []

    for action in actions:
        if action == "Invest":
            budget = min(cash * 0.35, current_price * 2)
            quantity = int(budget // current_price)
            if quantity == 0 and cash >= current_price:
                quantity = 1
            if quantity > 0:
                cash -= quantity * current_price
                shares += quantity
                activity.append({"action": action, "quantity": quantity, "price": current_price})
        elif action == "Divest":
            quantity = max(1, shares // 2) if shares else 0
            if quantity > 0:
                shares -= quantity
                cash += quantity * current_price
                activity.append({"action": action, "quantity": quantity, "price": current_price})
        elif action == "Buy shares":
            quantity = 1 if cash >= current_price else 0
            if quantity > 0:
                cash -= current_price
                shares += 1
                activity.append({"action": action, "quantity": 1, "price": current_price})
        elif action == "Sell shares":
            quantity = 1 if shares > 0 else 0
            if quantity > 0:
                shares -= 1
                cash += current_price
                activity.append({"action": action, "quantity": 1, "price": current_price})
        elif action == "Convert currency":
            transfer = round(min(cash * 0.05, 250.0), 2)
            if transfer > 0:
                cash -= transfer
                reserve += transfer
                activity.append({"action": action, "amount": transfer})
        else:
            activity.append({"action": action, "quantity": 0})

    end_value = cash + (shares * next_price) + reserve
    cycle_pnl = round(end_value - start_value, 2)
    updated = PortfolioState(
        cash=round(cash, 2),
        shares=shares,
        currency_reserve=round(reserve, 2),
        total_value=round(end_value, 2),
        cumulative_pnl=round(portfolio.cumulative_pnl + cycle_pnl, 2),
        last_price=next_price,
    )
    return updated, activity, cycle_pnl


def summarize_performance(cycle_pnls: Sequence[float]) -> Dict[str, float]:
    """Compute comparison metrics for profitability, loss reduction, and stability."""

    values = list(cycle_pnls)
    cumulative = round(sum(values), 2)
    stability = round(pstdev(values), 4) if len(values) > 1 else 0.0
    return {
        "cumulative_pnl": cumulative,
        "loss_abs": round(abs(min(cumulative, 0.0)), 2),
        "stability": stability,
        "cycles": len(values),
    }
