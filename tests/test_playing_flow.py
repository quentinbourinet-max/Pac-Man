"""TDD for the end-of-game flow wired from PlayingLevel (J1 + J11).

Headless integration tests (real scene, dummy SDL drivers): they assert the
three terminal transitions route to the end screen / life loss as decided in
O4 and required by M44/M46/M52/M53.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game_engine.core import Game  # noqa: E402


def make_level():
    game = Game()
    return game, game.registry["level"](game)


def test_timeout_loses_one_life_and_resets_without_ending() -> None:
    game, pl = make_level()
    pl.lives = 3
    pl.remaining_time = 0.0001
    pl.update(0.5)
    assert pl.lives == 2
    assert pl.remaining_time == pl.time_limit
    assert pl.go_to_scene is None


def test_timeout_on_last_life_is_game_over() -> None:
    game, pl = make_level()
    pl.lives = 1
    pl.remaining_time = 0.0001
    pl.update(0.5)
    assert pl.go_to_scene == "end_screen"
    assert game.final_won is False
    assert game.final_score == pl.score


def test_victory_after_last_level() -> None:
    game, pl = make_level()
    pl.level_id = 10
    pl.item_grid = [[0]]
    pl.update(0.1)
    assert pl.level_transition_timer > 0
    pl.update(3.0)
    assert pl.go_to_scene == "end_screen"
    assert game.final_won is True
