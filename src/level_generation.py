from mazegen import MazeGenerator
from typing import List
from pathlib import Path


class Map:
    def __init__(self, level: int):
        self.level = level

    def create(self) -> List[List[int]]:
        gen = MazeGenerator(
                                width=20,
                                height=20,
                                entry=(0, 0),
                                exit_=(19, 19),
                                perfect=False,
                                seed=self.level,
                                asked_algo="dfs",
                            )
        gen.generate()
        return (gen.grid)

    def save(self, grid: List[List[int]]):
        file = Path("data/levels")
        file.mkdir(parents=True, exist_ok=True)
        with open(f"data/levels/level_{self.level}", "w") as f:
            for row in grid:
                line = " ".join(map(str, row))
                f.write(line + "\n")
