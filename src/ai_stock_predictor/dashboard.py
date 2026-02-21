"""Minimal local-first HTML dashboard generator from JSONL logs."""

from __future__ import annotations

import json
from pathlib import Path


def build_dashboard(log_path: str | Path, output_path: str | Path) -> Path:
    entries = []
    log_file = Path(log_path)
    if log_file.exists():
        for line in log_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))

    rows = "\n".join(
        f"<tr><td>{e['timestamp']}</td><td>{e['model_version']}</td><td>{e['portfolio_value']:.2f}</td>"
        f"<td>{e['profit_loss']:.2f}</td><td>{','.join(e['actions'])}</td></tr>"
        for e in entries[-100:]
    )
    html = f"""
<html>
  <head><title>AI Stock Predictor Dashboard</title></head>
  <body>
    <h1>Prediction History</h1>
    <table border='1' cellpadding='4'>
      <tr><th>Timestamp</th><th>Model</th><th>Portfolio Value</th><th>P/L</th><th>Actions</th></tr>
      {rows}
    </table>
  </body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
