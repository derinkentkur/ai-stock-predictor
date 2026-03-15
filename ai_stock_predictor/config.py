"""Configuration objects for local-first simulation runs."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RuntimeSettings:
    """Tunable runtime settings with reproducible defaults."""

    output_count: int = 4
    candidate_count: int = 3
    random_seed: int = 17
    initial_cash: float = 10_000.0
    promotion_window: int = 2


@dataclass(frozen=True)
class RuntimePaths:
    """Resolved local filesystem layout for the simulation."""

    root: Path
    market_data_path: Path
    webpage_dir: Path
    log_dir: Path
    prediction_log_path: Path
    promotion_log_path: Path
    registry_path: Path
    dashboard_path: Path
    cloud_todo_path: Path

    @classmethod
    def from_root(
        cls,
        root: Path,
        log_dir: Optional[Path] = None,
        dashboard_path: Optional[Path] = None,
    ) -> "RuntimePaths":
        root = root.resolve()
        resolved_log_dir = (log_dir or (root / "logs")).resolve()
        resolved_dashboard_path = (
            dashboard_path or (root / "dashboards" / "local_dashboard.html")
        ).resolve()
        return cls(
            root=root,
            market_data_path=(root / "data" / "market" / "sample_market_data.csv").resolve(),
            webpage_dir=(root / "data" / "webpages").resolve(),
            log_dir=resolved_log_dir,
            prediction_log_path=(resolved_log_dir / "predictions.jsonl").resolve(),
            promotion_log_path=(resolved_log_dir / "promotions.jsonl").resolve(),
            registry_path=(resolved_log_dir / "model_registry.json").resolve(),
            dashboard_path=resolved_dashboard_path,
            cloud_todo_path=(root / "docs" / "CLOUD_TODO.md").resolve(),
        )
