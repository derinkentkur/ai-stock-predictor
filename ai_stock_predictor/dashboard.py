"""Static HTML dashboard generation from append-only runtime logs."""

from collections import defaultdict
import json
from pathlib import Path
from typing import Dict, List


def build_dashboard(
    prediction_records: List[Dict[str, object]],
    promotion_records: List[Dict[str, object]],
    registry: Dict[str, object],
    output_path: Path,
) -> Path:
    """Render a single-file local dashboard for monitoring model behavior."""

    performance = defaultdict(list)
    latest_by_model = {}
    for record in prediction_records:
        performance[record["model_id"]].append(
            {
                "cycle": record["cycle_index"],
                "total_value": record["portfolio_state"]["total_value"],
                "cycle_pnl": record["cycle_pnl"],
            }
        )
        latest_by_model[record["model_id"]] = record

    payload = {
        "registry": registry,
        "performance": performance,
        "latest": latest_by_model,
        "promotions": promotion_records,
        "cycles": sorted({record["cycle_index"] for record in prediction_records}),
        "ingestion": [
            {
                "cycle_index": record["cycle_index"],
                "model_id": record["model_id"],
                "webpage_path": record["inputs"]["webpage"]["path"],
                "webpage_sha256": record["inputs"]["webpage"]["sha256"],
                "actions": record["interpreted_actions"],
            }
            for record in prediction_records
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _render_html(payload)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _render_html(payload: Dict[str, object]) -> str:
    serialized = json.dumps(payload, sort_keys=True)
    primary_model = payload["registry"].get("primary_model_id", "n/a")
    total_predictions = len(payload["ingestion"])
    promotion_count = len(payload["promotions"])
    title = "AI Stock Predictor Dashboard"
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #f4efe4;
      --panel: rgba(255, 255, 255, 0.82);
      --ink: #132238;
      --accent: #be5a2c;
      --accent-soft: #ffd0b8;
      --line: rgba(19, 34, 56, 0.14);
      --success: #1b7f5b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(190, 90, 44, 0.18), transparent 24rem),
        radial-gradient(circle at right, rgba(27, 127, 91, 0.15), transparent 20rem),
        linear-gradient(160deg, #f4efe4 0%, #f8f4ec 45%, #ece5d3 100%);
      min-height: 100vh;
    }}
    main {{
      width: min(1100px, calc(100vw - 2rem));
      margin: 0 auto;
      padding: 2rem 0 3rem;
    }}
    h1 {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2.2rem, 5vw, 3.8rem);
      margin: 0 0 0.5rem;
      letter-spacing: -0.04em;
    }}
    p {{
      margin: 0 0 1rem;
      line-height: 1.5;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.8fr 1fr;
      gap: 1rem;
      margin-bottom: 1rem;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 1.2rem;
      padding: 1.1rem 1.2rem;
      backdrop-filter: blur(18px);
      box-shadow: 0 10px 30px rgba(19, 34, 56, 0.06);
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.9rem;
      margin-bottom: 1rem;
    }}
    .stat-value {{
      font-size: 1.8rem;
      font-weight: 700;
      margin-top: 0.3rem;
    }}
    .muted {{
      color: rgba(19, 34, 56, 0.68);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      text-align: left;
      padding: 0.7rem 0.4rem;
      vertical-align: top;
    }}
    th {{
      font-size: 0.82rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: rgba(19, 34, 56, 0.68);
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 1rem;
      margin-top: 1rem;
    }}
    .chart {{
      display: flex;
      flex-direction: column;
      gap: 0.7rem;
    }}
    .line {{
      display: grid;
      grid-template-columns: 10rem 1fr;
      gap: 0.8rem;
      align-items: center;
    }}
    .track {{
      position: relative;
      height: 0.6rem;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(19, 34, 56, 0.08);
    }}
    .fill {{
      position: absolute;
      inset: 0 auto 0 0;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--success));
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.25rem 0.55rem;
      border-radius: 999px;
      background: var(--accent-soft);
      font-size: 0.82rem;
      margin-right: 0.35rem;
      margin-bottom: 0.35rem;
    }}
    @media (max-width: 800px) {{
      .hero, .stats, .grid {{
        grid-template-columns: 1fr;
      }}
      .line {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <article class="panel">
        <h1>{title}</h1>
        <p class="muted">Local-first multimodel monitoring with binary webpage ingestion, structured market data, automatic candidate evolution, and autonomous promotion. Live trading is intentionally disabled.</p>
        <div class="chip">Primary model: {primary_model}</div>
      </article>
      <article class="panel">
        <p class="muted">Prediction log entries</p>
        <div class="stat-value">{total_predictions}</div>
        <p class="muted">Promotion events: {promotion_count}</p>
      </article>
    </section>
    <section class="stats">
      <article class="panel">
        <p class="muted">Archived primaries</p>
        <div class="stat-value" id="archivedCount">0</div>
      </article>
      <article class="panel">
        <p class="muted">Active models</p>
        <div class="stat-value" id="activeCount">0</div>
      </article>
      <article class="panel">
        <p class="muted">Tracked cycles</p>
        <div class="stat-value" id="cycleCount">0</div>
      </article>
    </section>
    <section class="grid">
      <article class="panel">
        <h2>Portfolio Performance</h2>
        <div class="chart" id="chart"></div>
      </article>
      <article class="panel">
        <h2>Promotion History</h2>
        <table>
          <thead>
            <tr><th>Cycle</th><th>From</th><th>To</th><th>Reason</th></tr>
          </thead>
          <tbody id="promotionRows"></tbody>
        </table>
      </article>
    </section>
    <section class="grid">
      <article class="panel">
        <h2>Latest Model Outputs</h2>
        <table>
          <thead>
            <tr><th>Model</th><th>Role</th><th>Outputs</th><th>Actions</th><th>P/L</th></tr>
          </thead>
          <tbody id="latestRows"></tbody>
        </table>
      </article>
      <article class="panel">
        <h2>Webpage Ingestion Activity</h2>
        <table>
          <thead>
            <tr><th>Cycle</th><th>Model</th><th>Webpage</th><th>Actions</th></tr>
          </thead>
          <tbody id="ingestionRows"></tbody>
        </table>
      </article>
    </section>
  </main>
  <script>
    const payload = {payload};

    document.getElementById("archivedCount").textContent = payload.registry.archived_primary_ids.length;
    document.getElementById("activeCount").textContent = payload.registry.active_model_ids.length;
    document.getElementById("cycleCount").textContent = payload.cycles.length;

    const allSeries = Object.entries(payload.performance).map(([modelId, series]) => {{
      const latest = series[series.length - 1] || {{ total_value: 0 }};
      return {{ modelId, totalValue: latest.total_value }};
    }});
    const maxValue = Math.max(...allSeries.map((entry) => entry.totalValue), 1);
    const chartRoot = document.getElementById("chart");
    allSeries
      .sort((left, right) => right.totalValue - left.totalValue)
      .forEach((entry) => {{
        const row = document.createElement("div");
        row.className = "line";
        const label = document.createElement("div");
        label.innerHTML = `<strong>${{entry.modelId}}</strong><div class="muted">$${{entry.totalValue.toFixed(2)}}</div>`;
        const track = document.createElement("div");
        track.className = "track";
        const fill = document.createElement("div");
        fill.className = "fill";
        fill.style.width = `${{Math.max(8, (entry.totalValue / maxValue) * 100)}}%`;
        track.appendChild(fill);
        row.appendChild(label);
        row.appendChild(track);
        chartRoot.appendChild(row);
      }});

    const promotionRows = document.getElementById("promotionRows");
    if (payload.promotions.length === 0) {{
      promotionRows.innerHTML = '<tr><td colspan="4" class="muted">No promotions yet.</td></tr>';
    }} else {{
      payload.promotions.forEach((promotion) => {{
        const row = document.createElement("tr");
        row.innerHTML = `<td>${{promotion.cycle_index}}</td><td>${{promotion.from_model_id}}</td><td>${{promotion.to_model_id}}</td><td>${{promotion.reason}}</td>`;
        promotionRows.appendChild(row);
      }});
    }}

    const latestRows = document.getElementById("latestRows");
    Object.values(payload.latest).forEach((record) => {{
      const row = document.createElement("tr");
      row.innerHTML = `<td>${{record.model_id}}</td><td>${{record.role}}</td><td>${{record.normalized_outputs.join(", ")}}</td><td>${{record.interpreted_actions.join(" | ")}}</td><td>$${{record.cycle_pnl.toFixed(2)}}</td>`;
      latestRows.appendChild(row);
    }});

    const ingestionRows = document.getElementById("ingestionRows");
    payload.ingestion.slice(-12).reverse().forEach((record) => {{
      const webpage = record.webpage_path.split("/").slice(-1)[0];
      const row = document.createElement("tr");
      row.innerHTML = `<td>${{record.cycle_index}}</td><td>${{record.model_id}}</td><td>${{webpage}}</td><td>${{record.actions.join(" | ")}}</td>`;
      ingestionRows.appendChild(row);
    }});
  </script>
</body>
</html>
""".format(
        title=title,
        primary_model=primary_model,
        total_predictions=total_predictions,
        promotion_count=promotion_count,
        payload=serialized,
    )
