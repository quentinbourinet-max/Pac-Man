"""Highscore persistence: thin interface over the ConfigParser score store."""
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .parser import ConfigParser


def load(parser: "ConfigParser", mode: str) -> list[dict[str, Any]]:
    """Return the sorted Top-10 entries for the given mode using the parser."""
    return parser.get_scores(parser.config.paths.highscores, mode)


def save(parser: "ConfigParser", mode: str, name: str, score: int) -> None:
    """Append and persist a score entry for the given mode using the parser."""
    parser.save_score(parser.config.paths.highscores, mode, name, score)
