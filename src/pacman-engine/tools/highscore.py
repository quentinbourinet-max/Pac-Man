"""Highscore persistence — thin interface over the config.json
scores section."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..tools.parser import ConfigParser


def load(parser: "ConfigParser", mode: str) -> list[dict]:
    """Return the sorted Top-10 entries for the given mode using the parser."""
    assert parser.config.paths is not None
    return parser.get_scores(parser.config.paths.highscores, mode)


def save(parser: "ConfigParser", mode: str, name: str, score: int) -> None:
    """Append and persist a score entry for the given mode using the parser."""
    assert parser.config.paths is not None
    parser.save_score(parser.config.paths.highscores, mode, name, score)
