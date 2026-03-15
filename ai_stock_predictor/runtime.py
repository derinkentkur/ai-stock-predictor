"""End-to-end orchestration for the local-first multimodel simulation."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Sequence

from .config import RuntimePaths, RuntimeSettings
from .contracts import interpret_actions, normalize_scores, validate_scores
from .dashboard import build_dashboard
from .ingestion import FEATURE_NAMES, InputBundle, build_input_bundle, list_webpages, load_market_data, select_webpage
from .modeling import ModelConfig, build_baseline_config, generate_candidate_configs, predict_raw_scores
from .persistence import append_jsonl, load_jsonl, write_json
from .portfolio import PortfolioState, apply_actions, summarize_performance


@dataclass
class ModelState:
    config: ModelConfig
    portfolio: PortfolioState
    cycle_pnls: List[float] = field(default_factory=list)
    outperformance_streak: int = 0

    def metrics(self) -> Dict[str, float]:
        return summarize_performance(self.cycle_pnls)


class SimulationRuntime:
    """Coordinates inputs, model execution, scoring, logging, and monitoring."""

    def __init__(self, paths: RuntimePaths, settings: RuntimeSettings) -> None:
        self.paths = paths
        self.settings = settings
        self.market_rows = load_market_data(paths.market_data_path)
        self.webpages = list_webpages(paths.webpage_dir)
        self.bundle_history = []  # type: List[InputBundle]
        self.baseline_config = build_baseline_config(
            seed=settings.random_seed,
            output_count=settings.output_count,
            feature_count=len(FEATURE_NAMES),
        )
        self.model_states = {
            self.baseline_config.model_id: ModelState(
                config=self.baseline_config,
                portfolio=PortfolioState.from_cash(
                    settings.initial_cash,
                    self.market_rows[0].close,
                ),
            )
        }
        self.primary_model_id = self.baseline_config.model_id
        self.archived_primary_ids = []  # type: List[str]
        self.retired_candidate_ids = []  # type: List[str]
        self.generation_index = 0
        self.previous_primary_actions = ["Wait / No action"]
        self._bootstrap_candidates()

    def run(self, cycles: int) -> Dict[str, object]:
        """Run the local-first simulation for the requested number of cycles."""

        available_cycles = max(len(self.market_rows) - 1, 0)
        target_cycles = min(cycles, available_cycles)
        for cycle_index in range(target_cycles):
            webpage = select_webpage(
                self.webpages,
                cycle_index,
                self.previous_primary_actions,
                self.settings.random_seed,
            )
            bundle = build_input_bundle(self.market_rows, cycle_index, webpage)
            self.bundle_history.append(bundle)
            cycle_records = self._run_cycle(bundle)
            primary_record = next(
                record for record in cycle_records if record["model_id"] == self.primary_model_id
            )
            self.previous_primary_actions = primary_record["interpreted_actions"]
            self._evolve_candidates()

        registry = self._registry_payload()
        write_json(self.paths.registry_path, registry)
        build_dashboard(
            prediction_records=load_jsonl(self.paths.prediction_log_path),
            promotion_records=load_jsonl(self.paths.promotion_log_path),
            registry=registry,
            output_path=self.paths.dashboard_path,
        )
        return {
            "cycles_ran": target_cycles,
            "primary_model_id": self.primary_model_id,
            "active_model_ids": registry["active_model_ids"],
            "dashboard_path": str(self.paths.dashboard_path),
            "prediction_log_path": str(self.paths.prediction_log_path),
        }

    def _bootstrap_candidates(self) -> None:
        for config in generate_candidate_configs(
            self.baseline_config,
            self.settings.candidate_count,
            self.generation_index,
        ):
            self._register_candidate(config)

    def _run_cycle(self, bundle: InputBundle) -> List[Dict[str, object]]:
        active_states = list(self.model_states.values())
        with ThreadPoolExecutor(max_workers=len(active_states)) as executor:
            predictions = list(executor.map(lambda state: self._predict(state.config, bundle), active_states))

        cycle_records = []
        for state, prediction in zip(active_states, predictions):
            updated_portfolio, execution_log, cycle_pnl = apply_actions(
                state.portfolio,
                prediction["actions"],
                bundle.market.close,
                bundle.next_close,
            )
            state.portfolio = updated_portfolio
            state.cycle_pnls.append(cycle_pnl)
            record = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "cycle_index": bundle.cycle_index,
                "model_id": state.config.model_id,
                "version": state.config.version,
                "role": state.config.role,
                "mutations": list(state.config.mutations),
                "raw_outputs": prediction["raw_outputs"],
                "normalized_outputs": prediction["normalized_outputs"],
                "interpreted_actions": prediction["actions"],
                "inputs": bundle.input_summary,
                "portfolio_state": {
                    "cash": updated_portfolio.cash,
                    "shares": updated_portfolio.shares,
                    "currency_reserve": updated_portfolio.currency_reserve,
                    "total_value": updated_portfolio.total_value,
                    "cumulative_pnl": updated_portfolio.cumulative_pnl,
                },
                "cycle_pnl": cycle_pnl,
                "execution_log": execution_log,
                "metrics": state.metrics(),
            }
            append_jsonl(self.paths.prediction_log_path, record)
            cycle_records.append(record)
        self._maybe_promote(bundle.cycle_index)
        return cycle_records

    def _predict(self, config: ModelConfig, bundle: InputBundle) -> Dict[str, object]:
        raw_outputs = predict_raw_scores(config, bundle.feature_vector)
        normalized_outputs = normalize_scores(raw_outputs)
        validate_scores(normalized_outputs)
        actions = interpret_actions(normalized_outputs)
        return {
            "raw_outputs": raw_outputs,
            "normalized_outputs": normalized_outputs,
            "actions": actions,
        }

    def _maybe_promote(self, cycle_index: int) -> None:
        primary_state = self.model_states[self.primary_model_id]
        primary_metrics = primary_state.metrics()
        candidates = [
            state
            for model_id, state in self.model_states.items()
            if model_id != self.primary_model_id and state.config.role == "candidate"
        ]
        for candidate_state in candidates:
            candidate_metrics = candidate_state.metrics()
            if _beats_primary(candidate_metrics, primary_metrics):
                candidate_state.outperformance_streak += 1
            else:
                candidate_state.outperformance_streak = 0
            if candidate_state.outperformance_streak >= self.settings.promotion_window:
                previous_primary_id = self.primary_model_id
                self.primary_model_id = candidate_state.config.model_id
                self.archived_primary_ids.append(previous_primary_id)
                candidate_state.outperformance_streak = 0
                promotion_record = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "cycle_index": cycle_index,
                    "from_model_id": previous_primary_id,
                    "to_model_id": self.primary_model_id,
                    "reason": "Higher profitability or lower sustained losses over the promotion window.",
                }
                append_jsonl(self.paths.promotion_log_path, promotion_record)
                break

    def _evolve_candidates(self) -> None:
        self.generation_index += 1
        next_candidate = generate_candidate_configs(self.baseline_config, 1, self.generation_index)[0]
        self._register_candidate(next_candidate)

        candidate_ids = [
            model_id
            for model_id, state in self.model_states.items()
            if state.config.role == "candidate"
        ]
        if len(candidate_ids) <= self.settings.candidate_count:
            return

        ranked_candidates = sorted(
            (self.model_states[model_id] for model_id in candidate_ids),
            key=lambda state: (
                state.metrics()["cumulative_pnl"],
                -state.metrics()["loss_abs"],
                -state.metrics()["stability"],
            ),
            reverse=True,
        )
        keep_ids = {state.config.model_id for state in ranked_candidates[: self.settings.candidate_count]}
        for candidate_id in candidate_ids:
            if candidate_id not in keep_ids and candidate_id != self.primary_model_id:
                self.retired_candidate_ids.append(candidate_id)
                del self.model_states[candidate_id]

    def _register_candidate(self, config: ModelConfig) -> None:
        state = ModelState(
            config=config,
            portfolio=PortfolioState.from_cash(self.settings.initial_cash, self.market_rows[0].close),
        )
        if self.bundle_history:
            for bundle in self.bundle_history:
                prediction = self._predict(config, bundle)
                updated_portfolio, _, cycle_pnl = apply_actions(
                    state.portfolio,
                    prediction["actions"],
                    bundle.market.close,
                    bundle.next_close,
                )
                state.portfolio = updated_portfolio
                state.cycle_pnls.append(cycle_pnl)
        self.model_states[config.model_id] = state

    def _registry_payload(self) -> Dict[str, object]:
        return {
            "primary_model_id": self.primary_model_id,
            "archived_primary_ids": list(self.archived_primary_ids),
            "retired_candidate_ids": list(self.retired_candidate_ids),
            "active_model_ids": sorted(self.model_states.keys()),
            "models": {
                model_id: {
                    "config": asdict(state.config),
                    "metrics": state.metrics(),
                    "portfolio": {
                        "cash": state.portfolio.cash,
                        "shares": state.portfolio.shares,
                        "currency_reserve": state.portfolio.currency_reserve,
                        "total_value": state.portfolio.total_value,
                        "cumulative_pnl": state.portfolio.cumulative_pnl,
                    },
                }
                for model_id, state in sorted(self.model_states.items())
            },
            "cloud_deployment": {
                "status": "TODO",
                "tracking_doc": str(self.paths.cloud_todo_path),
            },
        }


def _beats_primary(candidate_metrics: Dict[str, float], primary_metrics: Dict[str, float]) -> bool:
    candidate_pnl = candidate_metrics["cumulative_pnl"]
    primary_pnl = primary_metrics["cumulative_pnl"]
    if candidate_pnl > primary_pnl:
        return True
    if candidate_pnl == primary_pnl:
        return candidate_metrics["stability"] < primary_metrics["stability"]
    if candidate_pnl < 0 and primary_pnl < 0:
        return candidate_metrics["loss_abs"] < primary_metrics["loss_abs"]
    return False
