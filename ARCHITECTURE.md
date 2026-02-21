## AI Stock Predictor Architecture

### Runtime Flow

1. **Input ingestion** (`ingestion.py`)
   - Reads full webpage bytes.
   - Combines market prices, financial API signal, sentiment, and economic indicators.
   - Produces normalized feature vector.

2. **Multi-model evaluation** (`runtime.py`)
   - Loads one baseline model plus `N` mutated alternatives.
   - Each model predicts `outputs_per_model` values.
   - Each raw output is normalized to the discrete contract and mapped to an action.

3. **Portfolio simulation** (`portfolio.py`)
   - Uses simplified profitability-first logic.
   - Applies interpreted actions to a simulated cash/share state.

4. **Autonomous promotion** (`runtime.py`)
   - Compares models by `profit_loss` then `portfolio_value`.
   - If a candidate outperforms baseline, promotion is logged.

5. **Append-only observability** (`logging_store.py`, `dashboard.py`)
   - Prediction cycles are appended to `logs/predictions.jsonl`.
   - Promotion events are appended to `logs/promotions.jsonl`.
   - `dashboards/index.html` is regenerated from logs for monitoring.

### Guarantees

- Discrete output contract is always enforced before actions.
- Logs are append-only JSONL.
- No live trading execution is included.
- Model behavior is reproducible with fixed seeds.

### Cloud Deployment

- **TODO**: Add cloud deployment packaging after local validation.
