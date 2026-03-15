#!/usr/bin/env python3
"""Run the local-first AI stock predictor simulation."""

from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_stock_predictor import RuntimePaths, RuntimeSettings, SimulationRuntime


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, default=6, help="How many market cycles to simulate.")
    parser.add_argument("--outputs", type=int, default=4, help="Outputs per model.")
    parser.add_argument("--alternatives", type=int, default=3, help="Active alternative model count.")
    parser.add_argument("--seed", type=int, default=17, help="Reproducible runtime seed.")
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=ROOT / "logs",
        help="Append-only log directory.",
    )
    parser.add_argument(
        "--dashboard-path",
        type=Path,
        default=ROOT / "dashboards" / "local_dashboard.html",
        help="Static dashboard output path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = RuntimeSettings(
        output_count=args.outputs,
        candidate_count=args.alternatives,
        random_seed=args.seed,
    )
    paths = RuntimePaths.from_root(
        ROOT,
        log_dir=args.log_dir,
        dashboard_path=args.dashboard_path,
    )
    runtime = SimulationRuntime(paths=paths, settings=settings)
    summary = runtime.run(cycles=args.cycles)
    print("Cycles ran:", summary["cycles_ran"])
    print("Primary model:", summary["primary_model_id"])
    print("Active models:", ", ".join(summary["active_model_ids"]))
    print("Prediction log:", summary["prediction_log_path"])
    print("Dashboard:", summary["dashboard_path"])
    print("Cloud deployment: TODO in", paths.cloud_todo_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
