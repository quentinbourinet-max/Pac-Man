from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tools.parser import ConfigParser
from typing import List
from mazegen import MazeGenerator


class MazeAdapter:
    """Single boundary between the game and the maze-generator package.

    Adapt this class -- not the callers -- to the official A-Maze-ing
    package (loader adapts to the package, never the opposite).
    """

    def __init__(self, width: int, height: int, perfect: bool = False) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect

    def generate(self, seed: int | None) -> List[List[int]]:
        """Return a freshly generated wall-bitmask grid for ``seed``."""
        return self._build(seed)

    def _build(self, seed: int | None) -> List[List[int]]:
        """Concrete call into the ``mazegenerator`` package.

        The only point bound to the package interface: builds with
        ``size``/``perfect``/``entry_cell``/``exit_cell``/``seed`` and reads
        the grid via the ``.maze`` property. The package seeds
        deterministically only for ``seed > 0`` (0/None -> random maze); same
        wall-bitmask encoding as the rest (1=top, 2=right, 4=bottom, 8=left).
        """
        gen = MazeGenerator(
            width=self.width,
            height=self.height,
            perfect=self.perfect,
            entry=(0, 0),
            exit_=(self.width - 1, self.height - 1),
            seed=seed if seed is not None else 0,
            asked_algo="dfs"
            )
        grid = gen.generate()
        return grid  # type: ignore[no-any-return]


def generate_grid(parser: "ConfigParser", level: int) -> List[List[int]]:
    """Generate a fresh maze grid for a level, in memory (no persistence).

    Level 1 uses a fixed seed (reproducible); subsequent levels are randomly
    generated on each call (subject VI.1: only the first level is seeded).
    Returns [] on generator failure, which stays non-fatal for the caller.
    """
    try:
        width, height = parser.get_level_dims(level)
        adapter = MazeAdapter(width=width, height=height, perfect=False)
        return adapter.generate(parser.get_level_seed(level))
    except Exception as exc:
        print(f" /!\\ Could not generate level {level}: {exc}")
        return []
