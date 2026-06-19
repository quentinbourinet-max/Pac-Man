"""TDD for the EndScreen scene (J6): game-over / victory + name entry.

Covers M16/M46/M47/M52/M53 behaviour at the logic level (no display):
submit persists the entry, Enter transitions to the main menu, an empty
name falls back to a default, and the heading reflects win/lose.
"""

import pygame

from game_engine.scenes.end_screen import EndScreen
from game_engine.tools import highscore


class FakeGame:
    """Minimal duck-typed engine: only what EndScreen reads."""

    def __init__(self, score: int = 0, won: bool = False) -> None:
        self.width = 800
        self.height = 600
        self.final_score = score
        self.final_won = won


def make_end(tmp_path, score: int = 1000, won: bool = False) -> EndScreen:
    pygame.font.init()
    es = EndScreen(FakeGame(score, won))
    es.highscore_path = tmp_path / "hs.json"
    return es


def keydown(key: int, unicode: str = "") -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)


def test_submit_persists_entry(tmp_path) -> None:
    es = make_end(tmp_path, score=1234)
    for ch in "ZOE":
        es.input.feed_char(ch)
    es.submit()
    board = highscore.load(es.highscore_path)
    assert {"name": "ZOE", "score": 1234} in board


def test_enter_submits_and_returns_to_main_menu(tmp_path) -> None:
    es = make_end(tmp_path, score=500)
    for ch in "ABC":
        es.input.feed_char(ch)
    target = es.handle_events([keydown(pygame.K_RETURN, "\r")])
    assert target == "main_menu"
    assert {"name": "ABC", "score": 500} in highscore.load(es.highscore_path)


def test_handle_events_types_into_field(tmp_path) -> None:
    es = make_end(tmp_path)
    es.handle_events([keydown(pygame.K_a, "a"), keydown(pygame.K_b, "b")])
    assert es.input.value == "ab"


def test_heading_is_game_over_when_lost(tmp_path) -> None:
    es = make_end(tmp_path, won=False)
    assert es.heading == "GAME OVER"


def test_heading_is_victory_when_won(tmp_path) -> None:
    es = make_end(tmp_path, won=True)
    assert es.heading == "VICTORY!"


def test_empty_name_falls_back_to_default(tmp_path) -> None:
    es = make_end(tmp_path, score=50)
    es.submit()
    board = highscore.load(es.highscore_path)
    assert board[0]["name"] == "PLAYER"


def test_render_draws_onto_surface(tmp_path) -> None:
    es = make_end(tmp_path, won=True)
    surface = pygame.Surface((es.game.width, es.game.height))
    surface.fill((1, 2, 3))
    es.render(surface)
    changed = any(
        surface.get_at((x, y))[:3] != (1, 2, 3)
        for x in range(0, es.game.width, 40)
        for y in range(0, es.game.height, 40)
    )
    assert changed
