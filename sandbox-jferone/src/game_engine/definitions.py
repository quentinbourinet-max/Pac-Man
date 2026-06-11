"""Contracts every scene must honour, so the engine can swap them freely."""


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pygame import event, Surface

if TYPE_CHECKING:                       # avoids the core <-> definitions cycle
    from .core import Game

QUIT = "quit"


class Scene(ABC):
    """One screen of the program (menu, gameplay, ...).

    The engine keeps exactly one Scene active at a time and drives it through
    the same three calls every frame. A scene requests a transition by
    returning a target scene name (or QUIT) from handle_events; returning None
    means "stay on this scene".
    """

    def __init__(self, game: "Game") -> None:
        self.game = game

    @abstractmethod
    def handle_events(self, events: list[event.Event]) -> str | None:
        """React to input. Return a scene name / QUIT to transition or None."""
        ...

    @abstractmethod
    def update(self, framesync: float) -> None:
        """Advance scene state by the elapsed frame time (seconds)."""
        ...

    @abstractmethod
    def render(self, surface: Surface) -> None:
        """Draw the scene onto the given surface."""
        ...


# =============================================================================
