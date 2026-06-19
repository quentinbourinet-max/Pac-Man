"""TDD for the ScoresMenu scene (J3): Top-10 highscore board (M14/M17)."""

import json

import pygame

from game_engine.scenes.scores_menu import ScoresMenu


class FakeGame:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600


def make_scores() -> ScoresMenu:
    pygame.font.init()
    return ScoresMenu(FakeGame())


def keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def test_rows_are_ranked_name_score() -> None:
    sm = make_scores()
    sm.entries = [{"name": "ALICE", "score": 500},
                  {"name": "BOB", "score": 200}]
    assert sm.rows() == ["1. ALICE  500", "2. BOB  200"]


def test_empty_board_shows_placeholder() -> None:
    sm = make_scores()
    sm.entries = []
    assert sm.rows() == ["NO SCORES YET"]


def test_refresh_loads_sorted_top_ten(tmp_path) -> None:
    sm = make_scores()
    path = tmp_path / "hs.json"
    path.write_text(json.dumps(
        [{"name": f"P{i}", "score": i * 10} for i in range(15)]))
    sm.highscore_path = path
    sm.refresh()
    assert len(sm.entries) == 10
    assert sm.entries[0]["score"] == 140
    assert sm.entries[-1]["score"] == 50


def test_escape_returns_to_main_menu() -> None:
    sm = make_scores()
    assert sm.handle_events([keydown(pygame.K_ESCAPE)]) == "main_menu"


def test_click_returns_to_main_menu() -> None:
    sm = make_scores()
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    assert sm.handle_events([ev]) == "main_menu"


def test_render_draws_onto_surface() -> None:
    sm = make_scores()
    sm.entries = [{"name": "ZED", "score": 99}]
    surface = pygame.Surface((sm.game.width, sm.game.height))
    surface.fill((1, 2, 3))
    sm.render(surface)
    changed = any(
        surface.get_at((x, y))[:3] != (1, 2, 3)
        for x in range(0, sm.game.width, 40)
        for y in range(0, sm.game.height, 40)
    )
    assert changed
