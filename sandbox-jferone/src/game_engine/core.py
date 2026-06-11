"""Engine runtime: owns the window, the main loop and the active scene."""

import json
from pathlib import Path

import pygame

from .definitions import QUIT, Scene
from .scenes.main_menu import MainMenu
from .scenes.credits_menu import CreditsMenu

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class Game:
    """The single engine: one window, one loop, one active scene at a time."""

    def __init__(self) -> None:
        # json cfg extraction
        cfg = json.loads(CONFIG_PATH.read_text())["window"]
        self.width = cfg["width"]
        self.height = cfg["height"]
        self.fps = cfg["fps"]
        self.running = False

        # pygame cfg initialization
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(cfg["title"])
        self.clock = pygame.time.Clock()
        self.registry: dict[str, type[Scene]] = {
                                                "main_menu": MainMenu,
                                                "credits": CreditsMenu,
                                                }
        self.scene: Scene = self.registry["main_menu"](self)

    def change_scene(self, name: str) -> None:
        if name == QUIT:
            self.running = False
            return
        self.scene = self.registry[name](self)

    # Main Runtime
    def run(self) -> None:
        self.running = True
        while self.running:
            framesync = self.clock.tick(self.fps) / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            target = self.scene.handle_events(events)
            self.scene.update(framesync)
            self.scene.render(self.screen)
            pygame.display.flip()

            if target is not None:
                self.change_scene(target)

        pygame.quit()


def run() -> None:
    Game().run()


# =============================================================================
