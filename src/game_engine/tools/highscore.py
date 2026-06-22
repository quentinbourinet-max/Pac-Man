"""Highscore persistence - JSON file, robust to missing or corrupt data."""

import json
from pathlib import Path


def load(path: Path) -> list[dict[str, int | str]]:
    """Returns the refreshed/actual state of highscore."""
    try:
        data: dict[str, int | str] = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save(path: Path, name: str, score: int) -> None:
    """Loads the last state of highscore and saves the new entries on it."""
    entries = load(path)
    entries.append({"name": name[:10], "score": max(0, int(score))})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entries, indent=2))
    except OSError:
        pass
