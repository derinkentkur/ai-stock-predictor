# AI Stock Predictor

Local-first multi-model autonomous prediction simulator with strict discrete action outputs.

## Implemented Scope

- Multi-model inference (baseline + N alternatives) with outputs `1..N` per model.
- Strict score normalization to contract values: `0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.00`.
- Webpage binary ingestion + structured market/news/economic features.
- Continuous candidate generation through deterministic model mutation.
- Autonomous promotion when a candidate yields higher profitability or lower loss.
- Append-only JSONL logs for predictions and promotions.
- Minimal practical dashboard generated as local HTML from logs.
- Reproducible execution via explicit random seeds.
- Local-first execution; cloud deployment remains TODO.

## Quickstart

```bash
python -m ai_stock_predictor
```

Outputs:

- `logs/predictions.jsonl`
- `logs/promotions.jsonl`
- `dashboards/index.html`

## Development

```bash
python -m pip install -e .[dev]
pytest
```

## Discrete Output Contract

| Score | Action |
|---|---|
| 0.35 | invest |
| 0.30 | divest |
| 0.25 | buy_shares |
| 0.20 | sell_shares |
| 0.15 | convert_currency |
| 0.10 | explore_new_random_site |
| 0.05 | analyze_similar_site |
| 0.00 | wait |

Values are always normalized to this contract before action interpretation.
