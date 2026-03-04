from ai_stock_predictor.actions import ALLOWED_SCORES, interpret_score


def test_non_contract_values_become_wait() -> None:
    out = interpret_score(0.278)
    assert out.score in ALLOWED_SCORES
    assert out.score == 0.00
    assert out.action == "wait"


def test_exact_contract_value_is_preserved() -> None:
    out = interpret_score(0.25)
    assert out.score == 0.25
    assert out.action == "buy_shares"
