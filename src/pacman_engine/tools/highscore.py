"""Highscore persistence: thin interface over the ConfigParser score store."""
from typing import TYPE_CHECKING, Any
import json
if TYPE_CHECKING:
    from .parser import ConfigParser
from ..models.models import HighScoreEntry


class HighScoresTools:
    @staticmethod
    def validate_mode_scores(raw_entries: list) -> list:
        """Use the model to check each highscore entry and sort
        the wright ones"""
        valid_entries = []
        for entry in raw_entries:
            try:
                validated = HighScoreEntry(**entry)
                valid_entries.append(validated.model_dump())
            except Exception:
                pass
        valid_entries.sort(key=lambda x: x["score"], reverse=True)
        return valid_entries

    @classmethod
    def load(cls, parser: "ConfigParser", mode: str) -> list[dict[str, Any]]:
        """Load the scores, delete false entries and sort the wright ones"""
        assert parser.config.paths is not None
        raw_scores = parser.get_scores(parser.config.paths.highscores, mode)
        clean_scores = cls.validate_mode_scores(raw_scores)
        if len(clean_scores) != len(raw_scores):
            filepath = parser.config.paths.highscores
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            data[mode] = clean_scores
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        return clean_scores

    @classmethod
    def save(cls, parser: "ConfigParser", mode: str, name: str,
             score: int) -> None:
        """Append and persist a score entry for the given
        mode using the parser."""
        parser.save_score(parser.config.paths.highscores, mode, name, score)
