## Title

AI Stock Predictor — Multi-Model Autonomous Prediction System with Discrete 0.00–0.35 Action Outputs, Webpage Binary Inputs, and Continuous Model Evolution

---

## Overview

This issue defines the **complete intended architecture** for the AI stock predictor system.

The system will:

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

This is a master architectural issue describing system behavior, not a single PR.

---

# 1️⃣ Output Model Contract

## Multi-Model Outputs

* Multiple models run concurrently.
* Each model produces:

```
scores: List[float]  # outputs 1..N per model
```

## Allowed Score Values Only

Outputs must be restricted to:

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
* Output enforcement must happen in a normalization layer.

---

# 2️⃣ Data Input Layer

## Binary Webpage Feeding

The system must support:

* Feeding an entire webpage directly into the model as binary data.
* No partial scraping requirement — full page ingestion supported.
* Models may use:

  * 0.10 outputs → find random site
  * 0.05 outputs → analyze similar site for additional signals.

## Additional Inputs

Also support:

* Market price data
* Financial APIs
* News/sentiment sources
* Structured economic indicators.

All inputs should normalize into a common feature representation.

---

# 3️⃣ Multi-Model Comparison Architecture

The system always runs:

* Original baseline model
* N alternative models

Each produces its own output vector.

Comparison criteria:

* Profitability
* Loss reduction
* Prediction stability
* Overall performance improvement.

---

# 4️⃣ Automatic Alternative Model Generation

Alternative models are always generated during training by:

* Random modification of the original model
* Possible modifications include:

  * Architecture tweaks
  * Parameter mutations
  * Feature adjustments
  * Training window changes.

This is continuous, not scheduled manually.

---

# 5️⃣ Autonomous Model Promotion

Promotion rules:

* Fully automatic.
* No manual approval required.
* A candidate becomes primary if it:

  * Makes more money OR
  * Loses less money consistently.

Previous primary models must be archived.

All promotions must be logged.

---

# 6️⃣ Portfolio Logic (Initial Simplified Rule)

Primary evaluation metric:

> If the model makes money or loses less money, it is considered better.

Advanced trading constraints (risk models, exposure limits, etc.) are deferred.

### TODO

* Real trading execution integration.
* Risk management expansion.

---

# 7️⃣ Feedback Loop

Every prediction cycle must record:

* Model version
* Inputs used
* Raw outputs
* Normalized outputs
* Interpreted actions
* Portfolio state
* Resulting profit/loss.

This data feeds:

* Retraining
* Model comparison
* Long-term evaluation.

---

# 8️⃣ Monitoring / UI Requirements

Dashboard should be **practically useful**, not decorative.

Minimum features:

* Prediction outputs per model
* Portfolio performance tracking
* Model comparison metrics
* Model promotion history
* Historical prediction visualization (charts/timelines)
* Visibility into webpage ingestion activity.

Exact UI implementation flexible.

---

# 9️⃣ Deployment Strategy

### Phase 1 — Local First

* Primary development local.
* Minimal infrastructure assumptions.

### Phase 2 — Cloud (TODO)

* Cloud deployment optional after validation.
* Architecture should not block cloud scaling.

---

# 🔟 Technology Preferences

* Primary: Python ecosystem.
* Secondary languages allowed where beneficial.
* ML framework flexible but must support multimodel experimentation.

---

# Acceptance Criteria

* [ ] Multimodel inference producing outputs 1..N
* [ ] Outputs restricted to allowed discrete values
* [ ] Binary webpage ingestion functional
* [ ] Structured market data ingestion working
* [ ] Automatic alternative model generation operational
* [ ] Autonomous promotion mechanism functional
* [ ] Portfolio profitability tracking implemented
* [ ] Full prediction logging pipeline present
* [ ] Useful monitoring dashboard implemented
* [ ] Local-first deployment working
* [ ] Cloud deployment marked TODO.

---

# Key Principles

* Strict output action contract
* Continuous model self-improvement
* Profitability-first evaluation
* Autonomous operation
* Observability over opacity
* Flexible future deployment.

---

This issue represents the full intended AI stock predictor system architecture and lifecycle.
