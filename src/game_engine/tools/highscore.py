"""Highscore persistence — thin interface over the config.json scores section."""

from game_engine.config import get_scores, save_score


def load(mode: str) -> list[dict]:
    """Return the sorted Top-10 entries for the given mode."""
    return get_scores(mode)


def save(mode: str, name: str, score: int) -> None:
    """Append and persist a score entry for the given mode."""
    save_score(mode, name, score)
