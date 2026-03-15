"""Tests for the discrete score contract."""

import unittest

from ai_stock_predictor.contracts import ALLOWED_SCORES, interpret_actions, normalize_scores, validate_scores


class ContractTests(unittest.TestCase):
    def test_normalize_score_quantizes_to_allowed_values(self) -> None:
        normalized = normalize_scores([0.349, 0.281, 0.109, -1.0, 7.0])
        self.assertEqual(normalized, [0.35, 0.30, 0.10, 0.00, 0.35])
        validate_scores(normalized)

    def test_interpret_actions_matches_contract(self) -> None:
        actions = interpret_actions(ALLOWED_SCORES)
        self.assertEqual(actions[0], "Invest")
        self.assertEqual(actions[-1], "Wait / No action")


if __name__ == "__main__":
    unittest.main()
