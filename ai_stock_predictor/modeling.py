"""Deterministic baseline and evolved candidate model generation."""

from dataclasses import dataclass
from math import exp
import random
from typing import Iterable, List, Sequence, Tuple

from .contracts import normalize_scores


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    version: str
    role: str
    seed: int
    output_count: int
    feature_count: int
    weights: Tuple[Tuple[float, ...], ...]
    bias: Tuple[float, ...]
    lookback_window: int
    architecture: str
    mutations: Tuple[str, ...]


ARCHITECTURES = ("balanced", "momentum", "contrarian")


def build_baseline_config(seed: int, output_count: int, feature_count: int) -> ModelConfig:
    """Create a reproducible baseline model config."""

    rng = random.Random(seed)
    weights = _build_weight_matrix(rng, output_count, feature_count)
    bias = tuple(round(rng.uniform(-0.25, 0.25), 6) for _ in range(output_count))
    return ModelConfig(
        model_id="baseline-v1",
        version="baseline-v1",
        role="baseline",
        seed=seed,
        output_count=output_count,
        feature_count=feature_count,
        weights=weights,
        bias=bias,
        lookback_window=3,
        architecture="balanced",
        mutations=(),
    )


def generate_candidate_configs(
    baseline_config: ModelConfig,
    count: int,
    generation_index: int,
) -> List[ModelConfig]:
    """Create deterministic candidate configs from the original baseline."""

    configs = []
    for offset in range(count):
        seed = baseline_config.seed + (generation_index * 100) + offset + 1
        rng = random.Random(seed)
        mutations = []
        architecture = rng.choice(ARCHITECTURES)
        if architecture != baseline_config.architecture:
            mutations.append("architecture:%s" % architecture)
        lookback_window = rng.choice((1, 3, 5))
        if lookback_window != baseline_config.lookback_window:
            mutations.append("lookback:%s" % lookback_window)
        weights = []
        for row in baseline_config.weights:
            mutated_row = []
            for weight in row:
                jitter = rng.uniform(-0.12, 0.12)
                mutated_row.append(round(weight + jitter, 6))
            weights.append(tuple(mutated_row))
        bias = []
        for value in baseline_config.bias:
            bias_shift = rng.uniform(-0.08, 0.08)
            bias.append(round(value + bias_shift, 6))
        configs.append(
            ModelConfig(
                model_id="candidate-g%s-m%s" % (generation_index, offset),
                version="candidate-g%s-m%s" % (generation_index, offset),
                role="candidate",
                seed=seed,
                output_count=baseline_config.output_count,
                feature_count=baseline_config.feature_count,
                weights=tuple(weights),
                bias=tuple(bias),
                lookback_window=lookback_window,
                architecture=architecture,
                mutations=tuple(mutations or ("parameter:jitter",)),
            )
        )
    return configs


def predict_raw_scores(config: ModelConfig, feature_vector: Sequence[float]) -> List[float]:
    """Predict continuous scores before the normalization layer enforces the contract."""

    outputs = []
    for output_index in range(config.output_count):
        linear_signal = config.bias[output_index]
        for feature_index, feature_value in enumerate(feature_vector):
            linear_signal += config.weights[output_index][feature_index] * feature_value
        window_signal = _window_signal(feature_vector, config.lookback_window)
        if config.architecture == "momentum":
            linear_signal += 0.35 * window_signal
        elif config.architecture == "contrarian":
            linear_signal -= 0.35 * window_signal
        probability = 1.0 / (1.0 + exp(-linear_signal))
        outputs.append(round(probability * 0.35, 6))
    return outputs


def predict_discrete_scores(config: ModelConfig, feature_vector: Sequence[float]) -> List[float]:
    """Predict contract-safe discrete scores."""

    return normalize_scores(predict_raw_scores(config, feature_vector))


def _build_weight_matrix(
    rng: random.Random,
    output_count: int,
    feature_count: int,
) -> Tuple[Tuple[float, ...], ...]:
    rows = []
    for _ in range(output_count):
        row = tuple(round(rng.uniform(-1.25, 1.25), 6) for _ in range(feature_count))
        rows.append(row)
    return tuple(rows)


def _window_signal(feature_vector: Iterable[float], lookback_window: int) -> float:
    feature_vector = list(feature_vector)
    if lookback_window == 1:
        return feature_vector[1]
    if lookback_window == 3:
        return feature_vector[3]
    return feature_vector[4]
