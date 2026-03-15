"""Integration tests for the local-first runtime."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ai_stock_predictor import RuntimePaths, RuntimeSettings, SimulationRuntime
from ai_stock_predictor.modeling import build_baseline_config, generate_candidate_configs
from ai_stock_predictor.persistence import append_jsonl, load_jsonl


ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def test_candidate_generation_is_reproducible(self) -> None:
        baseline = build_baseline_config(seed=17, output_count=4, feature_count=13)
        left = generate_candidate_configs(baseline, count=2, generation_index=2)
        right = generate_candidate_configs(baseline, count=2, generation_index=2)
        self.assertEqual(left, right)

    def test_append_only_logging_preserves_existing_records(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "predictions.jsonl"
            append_jsonl(path, {"cycle": 1})
            append_jsonl(path, {"cycle": 2})
            records = load_jsonl(path)
            self.assertEqual([record["cycle"] for record in records], [1, 2])

    def test_runtime_creates_logs_registry_and_dashboard(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            log_dir = tmp_root / "logs"
            dashboard_path = tmp_root / "dashboards" / "dashboard.html"
            paths = RuntimePaths.from_root(ROOT, log_dir=log_dir, dashboard_path=dashboard_path)
            settings = RuntimeSettings(output_count=4, candidate_count=3, random_seed=17)
            runtime = SimulationRuntime(paths=paths, settings=settings)
            summary = runtime.run(cycles=5)

            self.assertEqual(summary["cycles_ran"], 5)
            prediction_records = load_jsonl(paths.prediction_log_path)
            self.assertGreaterEqual(len(prediction_records), 20)
            for record in prediction_records:
                self.assertEqual(len(record["normalized_outputs"]), 4)
                self.assertTrue(all(output in [0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.00] for output in record["normalized_outputs"]))

            self.assertTrue(paths.registry_path.exists())
            self.assertTrue(paths.dashboard_path.exists())
            dashboard_html = paths.dashboard_path.read_text(encoding="utf-8")
            self.assertIn("AI Stock Predictor Dashboard", dashboard_html)


if __name__ == "__main__":
    unittest.main()
