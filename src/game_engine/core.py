"""Engine runtime: owns the window, the main loop and the active scene."""

import pygame
from .config import get_cfg
from .definitions import QUIT, PAUSE, CLOSE, Scene, Overlay
from .scenes.main_menu import MainMenu
from .scenes.instructions_menu import InstructionsMenu
from .scenes.playing_level import PlayingLevel
from .scenes.end_screen import EndScreen
from .scenes.scores_menu import ScoresMenu
from .ui.pause_hud import PauseOverlay


class Game:
    """The single engine: one window, one loop, one active scene at a time."""

    def __init__(self) -> None:
        cfg = get_cfg().get("window", {})
        self.width = cfg.get("width", 800)
        self.height = cfg.get("height", 600)
        self.fps = cfg.get("fps", 60)
        self.running = False
        self.final_score = 0
        self.final_won = False

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(cfg.get("title", "Pac-Man"))
        self.clock = pygame.time.Clock()
        self.registry: dict[str, type[Scene]] = {
                                            "main_menu": MainMenu,
                                            "instructions": InstructionsMenu,
                                            "level": PlayingLevel,
                                            "end_screen": EndScreen,
                                            "scores": ScoresMenu
                                            }
        self.scene: Scene = self.registry["main_menu"](self)
        self.overlay: Overlay | None = None

    def change_scene(self, name: str) -> None:
        if name == QUIT:
            self.running = False
            return
        self.scene = self.registry[name](self)

    def open_overlay(self, overlay: Overlay) -> None:
        self.overlay = overlay

    def _apply_target(self, target: str | None) -> None:
        if self.overlay is not None:
            if target is not None:
                self.overlay.on_close()
                self.overlay = None
                if target != CLOSE:
                    self.change_scene(target)
            return
        if target == PAUSE:
            self.open_overlay(PauseOverlay(self))
        elif target is not None:
            self.change_scene(target)

    def step(self, events: list[pygame.event.Event],
             framesync: float) -> None:
        if self.overlay is not None:
            target = self.overlay.handle_events(events)
        else:
            target = self.scene.handle_events(events)
            self.scene.update(framesync)
        self._apply_target(target)

    def run(self) -> None:
        self.running = True
        while self.running:
            framesync = self.clock.tick(self.fps) / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.step(events, framesync)
            self.scene.render(self.screen)
            if self.overlay is not None:
                self.overlay.render(self.screen)
            pygame.display.flip()
        pygame.quit()


def run() -> None:
    Game().run()
