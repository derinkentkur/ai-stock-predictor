## Title

AI Stock Predictor — Multi-Model Autonomous Prediction System with Discrete 0.00–0.35 Action Outputs, Webpage Binary Inputs, and Continuous Model Evolution

---

## Overview

This document describes the target architecture and current implementation shape.

The system is designed to:

* Run multiple AI models simultaneously
* Produce **N outputs per model** (outputs 1..N)
* Restrict outputs to **specific discrete values between 0.00 and 0.35**
* Map those values to operational actions
* Ingest full webpages as binary inputs plus structured market data
* Continuously generate alternative models via randomized modification
* Automatically promote better-performing models
* Track portfolio performance primarily by profitability
* Provide a useful monitoring dashboard
* Operate local-first (cloud deployment later as TODO)

---

## 1️⃣ Output Model Contract

### Multi-Model Outputs

* Multiple models run concurrently.
* Each model produces:

```
scores: List[float]  # outputs 1..N per model
```

### Allowed Score Values Only

Outputs are restricted to:

| Score | Meaning                 |
|-------|-------------------------|
| 0.35  | Invest                  |
| 0.30  | Divest                  |
| 0.25  | Buy shares              |
| 0.20  | Sell shares             |
| 0.15  | Convert currency        |
| 0.10  | Explore new/random site |
| 0.05  | Analyze similar site    |
| 0.00  | Wait / No action        |

Important rules:

* Values between these numbers intentionally do nothing.
* Adding new actions requires retraining.
* Output enforcement happens in a normalization layer.

---

## 2️⃣ Data Input Layer

* Full webpage ingestion as raw binary bytes.
* Structured inputs:
  * Market price data
  * Financial APIs
  * News/sentiment
  * Structured economic indicators
* Inputs normalize into a common feature representation.

---

## 3️⃣ Multi-Model Comparison Architecture

Runtime executes:

* Original baseline model
* N alternative models

Comparison criteria:

* Profitability
* Loss reduction
* Prediction stability
* Overall performance improvement

---

## 4️⃣ Automatic Alternative Model Generation

Alternative models are generated continuously by randomized modifications:

* Architecture/parameter tweaks
* Feature adjustments
* Training window changes

Current implementation provides deterministic mutation for reproducibility.

---

## 5️⃣ Autonomous Model Promotion

Promotion rules:

* Fully automatic
* Candidate becomes primary if it:
  * Makes more money, or
  * Loses less money consistently
* Previous primary model/version is retained in logs
* All promotions are logged

---

## 6️⃣ Portfolio Logic (Initial Simplified Rule)

Primary evaluation metric:

> If the model makes money or loses less money, it is considered better.

Advanced constraints remain future work.

### TODO

* Real trading execution integration (not implemented)
* Risk management expansion

---

## 7️⃣ Feedback Loop

Every prediction cycle records:

* Model version
* Inputs used
* Raw outputs
* Normalized outputs
* Interpreted actions
* Portfolio state
* Resulting profit/loss

Logs are append-only JSONL files.

---

## 8️⃣ Monitoring / UI

A practical local dashboard includes:

* Prediction outputs per model
* Portfolio performance snapshots
* Model comparison visibility
* Promotion history visibility
* Historical prediction table
* Webpage ingestion visibility (input metadata)

---

## 9️⃣ Deployment Strategy

### Phase 1 — Local First

* Primary development local
* Minimal infrastructure assumptions

### Phase 2 — Cloud (TODO)

* Cloud deployment optional after validation
* Architecture should not block cloud scaling

---

## 🔟 Current Module Mapping

* `src/ai_stock_predictor/actions.py` — output contract normalization + action mapping
* `src/ai_stock_predictor/ingestion.py` — binary + structured input bundle and features
* `src/ai_stock_predictor/models.py` — baseline/mutated reproducible model specs
* `src/ai_stock_predictor/portfolio.py` — simulation-only portfolio updates
* `src/ai_stock_predictor/runtime.py` — cycle execution, evaluation, promotion, logging trigger
* `src/ai_stock_predictor/logging_store.py` — append-only JSONL writer
* `src/ai_stock_predictor/dashboard.py` — local HTML dashboard generation
