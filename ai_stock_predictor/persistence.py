"""Append-only prediction logging and runtime state persistence."""

from pathlib import Path
import json
from typing import Dict, Iterable, List


def append_jsonl(path: Path, record: Dict[str, object]) -> None:
    """Append one JSON object to a JSONL file without rewriting existing records."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")


def load_jsonl(path: Path) -> List[Dict[str, object]]:
    """Load JSONL records if the file exists."""

    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def write_json(path: Path, payload: Dict[str, object]) -> None:
    """Write a compact snapshot file for the latest runtime state."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
