"""Deterministic toy models and mutation for reproducible experiments."""

from __future__ import annotations

from dataclasses import dataclass
import random

from .actions import ALLOWED_SCORES


@dataclass(frozen=True)
class ModelSpec:
    version: str
    weights: tuple[float, ...]
    bias: float
    seed: int

    def predict(self, features: list[float], outputs: int) -> list[float]:
        """Generate contract-compliant scores deterministically."""
        rng = random.Random(self.seed + int(sum(features) * 10_000))
        values: list[float] = []
        for index in range(outputs):
            signal = self.bias
            for weight_index, weight in enumerate(self.weights):
                feature = features[weight_index % len(features)]
                signal += weight * feature
            signal += rng.uniform(-0.15, 0.15)
            signal += (index * 0.02) - 0.03

            # Map deterministic signal into one of the allowed bins (exact contract value).
            bounded = max(0.0, min(0.35, signal))
            bucket = int(round((bounded / 0.35) * (len(ALLOWED_SCORES) - 1)))
            score = ALLOWED_SCORES[bucket]
            values.append(score)
        return values


def baseline_model(seed: int = 7) -> ModelSpec:
    return ModelSpec(version="baseline-v1", weights=(0.35, -0.20, 0.12, 0.05), bias=0.18, seed=seed)


def mutate_model(source: ModelSpec, mutation_id: int, rng: random.Random) -> ModelSpec:
    candidate_weights = list(source.weights)
    idx = rng.randrange(len(candidate_weights))
    candidate_weights[idx] += rng.uniform(-0.09, 0.09)
    candidate_bias = source.bias + rng.uniform(-0.04, 0.04)

    candidate_bias = max(min(candidate_bias, max(ALLOWED_SCORES)), min(ALLOWED_SCORES))
    return ModelSpec(
        version=f"{source.version}-alt-{mutation_id}",
        weights=tuple(candidate_weights),
        bias=candidate_bias,
        seed=source.seed + mutation_id,
    )
