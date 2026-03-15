# Cloud Deployment TODO

Cloud deployment is intentionally deferred for the current local-first milestone.

## Next steps

- Containerize the runtime and static dashboard generator.
- Move append-only logs to a durable object store or database.
- Replace local sample inputs with authenticated external data sources.
- Add environment-based secret management for future API access.
- Introduce queue-based retraining and promotion workers.

## Guardrails

- Preserve the discrete output contract.
- Keep prediction logs append-only.
- Do not add live trading execution without a separate design review.
- Maintain reproducibility through explicit seeds and versioned configs.
