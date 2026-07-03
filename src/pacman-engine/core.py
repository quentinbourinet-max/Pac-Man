"""Engine runtime: owns the window, the main loop and the active scene."""

import pygame
import asyncio
from pathlib import Path
from .definitions import QUIT, Scene
from .scenes.main_menu import MainMenu
from .scenes.playing_level import PlayingLevel
from .scenes.pause_menu import PauseMenu
from .scenes.instructions_menu import InstructionsMenu
from .scenes.scores_menu import ScoresMenu
from .scenes.end_screen import EndScreen
from .tools.parser import ConfigParser


class Game:
    """The single engine: one window, one loop, one active scene at a time."""

    def __init__(self, custom_config_path: Path | None = None) -> None:
        self.parser = ConfigParser(custom_config_path)
        self.config = self.parser.config
        assert self.config.paths is not None
        self.parser.ensure_highscores_initialized(
            self.config.paths.highscores)
        self.width = self.config.window.width
        self.height = self.config.window.height
        self.fps = self.config.window.fps
        self.running = False

        pygame.init()
        self._windowed_size = (self.width, self.height)
        self.fullscreen = False
        self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption(self.config.window.title)
        self.clock = pygame.time.Clock()
        self.registry: dict[str, type[Scene]] = {
            "main_menu": MainMenu,
            "level": PlayingLevel,
            "instructions": InstructionsMenu,
            "scores": ScoresMenu,
            "end_screen": EndScreen
        }
        self.mode: str = "original"
        self.final_score: int = 0
        self.final_won: bool = False
        self.paused_scene: Scene | None = None
        self.scene: Scene = self.registry["main_menu"](self)

    def toggle_fullscreen(self) -> None:
        """Switch windowed/fullscreen (F11). Scenes re-layout from w/h."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self._windowed_size)
        self.width, self.height = self.screen.get_size()

    def change_scene(self, name: str) -> None:
        """Game scene changer."""
        if name == QUIT:
            self.running = False
            return
        self.paused_scene = None
        self.scene = self.registry[name](self)

    def pause_game(self) -> None:
        """Pause the game: create a PauseMenu while keeping the play scene."""
        screenshot = self.screen.copy()
        self.paused_scene = self.scene
        self.scene = PauseMenu(self,
                               background_surface=screenshot)  # type: ignore
        pygame.mixer.music.pause()

    def resume_game(self) -> None:
        """Return to the saved play scene."""
        if self.paused_scene:
            self.scene = self.paused_scene
            self.paused_scene = None
            pygame.mixer.music.unpause()

    async def run(self) -> None:
        """Core function for runtime ignition loop maintenance."""
        self.running = True
        while self.running:
            framesync = self.clock.tick(self.fps) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                      and event.key == pygame.K_F11):
                    self.toggle_fullscreen()

            target = self.scene.handle_events(events)
            self.scene.update(framesync)
            self.scene.render(self.screen)  # type: ignore
            pygame.display.flip()
            if target is not None:
                self.change_scene(target)
            await asyncio.sleep(0)

        pygame.quit()
