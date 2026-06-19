"""TDD for the TextInput widget core logic (M12: name entry constraints).

These tests cover the pure logic only (feed_char / backspace / value),
with no pygame display required (font passed as None).
"""

import pygame

from game_engine.ui.components import TextInput


def make_input(max_length: int = 10) -> TextInput:
    return TextInput((0, 0), (100, 40), None, max_length=max_length)


def keydown(key: int, unicode: str = "") -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)


def test_feed_char_accepts_ascii_letter() -> None:
    ti = make_input()
    ti.feed_char("a")
    assert ti.value == "a"


def test_feed_char_stops_at_max_length() -> None:
    ti = make_input(max_length=3)
    for ch in "abcdef":
        ti.feed_char(ch)
    assert ti.value == "abc"


def test_feed_char_rejects_symbol() -> None:
    ti = make_input()
    ti.feed_char("!")
    assert ti.value == ""


def test_feed_char_rejects_accented() -> None:
    ti = make_input()
    ti.feed_char("é")
    assert ti.value == ""


def test_feed_char_allows_space() -> None:
    ti = make_input()
    for ch in "a b":
        ti.feed_char(ch)
    assert ti.value == "a b"


def test_feed_char_allows_digit() -> None:
    ti = make_input()
    ti.feed_char("7")
    assert ti.value == "7"


def test_backspace_removes_last_char() -> None:
    ti = make_input()
    for ch in "abc":
        ti.feed_char(ch)
    ti.backspace()
    assert ti.value == "ab"


def test_backspace_on_empty_is_noop() -> None:
    ti = make_input()
    ti.backspace()
    assert ti.value == ""


def test_handle_event_feeds_typed_char() -> None:
    ti = make_input()
    ti.handle_event(keydown(pygame.K_a, "a"))
    assert ti.value == "a"


def test_handle_event_backspace_removes_last() -> None:
    ti = make_input()
    for ch in "ab":
        ti.feed_char(ch)
    ti.handle_event(keydown(pygame.K_BACKSPACE, "\x08"))
    assert ti.value == "a"


def test_handle_event_ignores_mouse_motion() -> None:
    ti = make_input()
    ti.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(5, 5)))
    assert ti.value == ""


def test_render_does_not_crash() -> None:
    pygame.font.init()
    font = pygame.font.Font(None, 18)
    ti = TextInput((50, 25), (100, 40), font)
    ti.feed_char("a")
    surface = pygame.Surface((200, 60))
    assert ti.render(surface) is None
