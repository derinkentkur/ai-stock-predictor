# AI Stock Predictor

Multi-Model Autonomous Prediction System with Discrete 0.00–0.35 Action Outputs, Webpage Binary Inputs, and Continuous Model Evolution.

---

## Overview

AI Stock Predictor is a local-first experimental system designed to:

* Run multiple AI models simultaneously
* Produce N outputs per model (outputs 1..N)
* Restrict outputs to discrete values between 0.00 and 0.35
* Map outputs to operational actions
* Ingest full webpages as binary inputs alongside structured market data
* Continuously generate alternative models via randomized modification
* Automatically promote better-performing models
* Track portfolio performance primarily by profitability
* Provide a practical monitoring dashboard

This repository focuses on autonomous model experimentation and profitability-driven evaluation.

For full architectural details, see `ARCHITECTURE.md`.

---

# Core Concepts

## 1. Discrete Action Output Contract

Each model produces:

```
scores: List[float]
```

Outputs are restricted to the following discrete values:

| Score | Action                  |
|-------|-------------------------|
| 0.35  | Invest                  |
| 0.30  | Divest                  |
| 0.25  | Buy shares              |
| 0.20  | Sell shares             |
| 0.15  | Convert currency        |
| 0.10  | Explore new/random site |
| 0.05  | Analyze similar site    |
| 0.00  | Wait / No action        |

All outputs pass through a normalization layer before action execution.

Values outside this contract must not trigger actions.

---

## 2. Multi-Model Runtime

At runtime the system executes:

* 1 baseline model
* N alternative models

Each model produces its own output vector and is evaluated independently.

Primary evaluation criteria:

* Profitability
* Loss reduction
* Stability

---

## 3. Continuous Model Evolution

Alternative models are generated automatically during training using strategies such as:

* Architecture variation
* Parameter mutation
* Feature adjustments
* Training window changes

If a candidate model performs better (more profit or consistently lower loss), it is automatically promoted.

Promotion events are logged.

---

## 4. Data Inputs

The system supports:

* Full webpage ingestion as raw binary
* Market price data
* Financial APIs
* News / sentiment sources
* Structured economic indicators

All inputs are normalized into a common feature representation before model ingestion.

---

## 5. Portfolio Evaluation (Initial Rule)

Current simplified rule:

> A model is better if it makes more money or loses less money.

Advanced risk management and real trading execution are future enhancements.

---

## 6. Feedback & Logging

Every prediction cycle records:

* Model version
* Inputs used
* Raw outputs
* Normalized outputs
* Interpreted actions
* Portfolio state
* Profit / loss outcome

This data supports retraining, comparison, and long-term evaluation.

---

## 7. Monitoring Dashboard

Minimum dashboard functionality includes:

* Model prediction outputs
* Portfolio performance charts
* Model comparison metrics
* Promotion history
* Historical prediction visualization
* Webpage ingestion visibility

---

# Deployment Strategy

## Phase 1 — Local First

* Runs on a single local machine
* Minimal infrastructure assumptions

## Phase 2 — Cloud (Future)

* Optional cloud deployment
* Architecture designed to remain cloud-compatible

---

# Technology Preferences

* Primary ecosystem: Python
* ML framework flexible
* Must support multimodel experimentation and reproducibility

---

# Repository Structure (Suggested)

```
README.md
ARCHITECTURE.md
AGENTS.md
models/
data/
training/
dashboards/
docs/
```

---

# Status

This project defines a continuous autonomous experimentation system for AI-driven stock prediction and model evolution.

Refer to `ARCHITECTURE.md` for the complete system design and lifecycle specification.
