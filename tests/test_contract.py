from ai_stock_predictor.actions import ALLOWED_SCORES, interpret_score


def test_normalization_sticks_to_allowed_scores() -> None:
    out = interpret_score(0.278)
    assert out.score in ALLOWED_SCORES
    assert out.action == "divest"
