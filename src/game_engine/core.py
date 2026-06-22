"""Engine runtime: owns the window, the main loop and the active scene."""

import json
from pathlib import Path
import pygame
from .definitions import QUIT, Scene
from .scenes.main_menu import MainMenu
from .scenes.playing_level import PlayingLevel
from .scenes.pause_menu import PauseMenu
from .scenes.instructions_menu import InstructionsMenu
from .scenes.scores_menu import ScoresMenu
from .scenes.end_screen import EndScreen

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "data" \
    / "config.json"


class Game:
    """The single engine: one window, one loop, one active scene at a time."""

    def __init__(self) -> None:
        cfg = json.loads(CONFIG_PATH.read_text())["window"]
        self.width = cfg["width"]
        self.height = cfg["height"]
        self.fps = cfg["fps"]
        self.running = False

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(cfg["title"])
        self.clock = pygame.time.Clock()
        self.registry: dict[str, type[Scene]] = {
                                            "main_menu": MainMenu,
                                            "level": PlayingLevel,
                                            "instructions": InstructionsMenu,
                                            "scores": ScoresMenu,
                                            "end_screen": EndScreen
                                            }
        self.scene: Scene = self.registry["main_menu"](self)
        self.paused_scene = None

    def change_scene(self, name: str) -> None:
        if name == QUIT:
            self.running = False
            return
        self.paused_scene = None
        self.scene = self.registry[name](self)

    def pause_game(self):
        """Met en pause en créant une PauseMenu
        et en gardant la scène de jeu."""
        screenshot = self.screen.copy()
        self.paused_scene = self.scene
        self.scene = PauseMenu(self, background_surface=screenshot)
        pygame.mixer.music.pause()

    def resume_game(self):
        """Revient à la scène de jeu sauvegardée."""
        if self.paused_scene:
            self.scene = self.paused_scene
            self.paused_scene = None
            pygame.mixer.music.unpause()

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
