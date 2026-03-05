from dataclasses import dataclass
from enum import Enum
from typing import Final

class GridCell(Enum):
    GRASS = 0
    BUSH = 1
    CRYSTAL = 2


@dataclass(frozen=True)
class Map:
    width: int
    height: int
    player_start_x: int
    player_start_y: int
    grid: tuple[tuple[GridCell, ...], ...]

    def get_cell(self, x: int, y: int) -> GridCell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("Position hors de la map")
        return self.grid[y][x]

def _make_map_decouverte() -> Map:
    width = 40
    height = 20

    # tout en herbe
    grid = [[GridCell.GRASS for _ in range(width)] for _ in range(height)]

    # buissons (comme avant)
    for (x, y) in [(3, 6), (7, 2), (2, 10), (3, 8)]:
        grid[y][x] = GridCell.BUSH

    # cristaux (comme avant)
    for (x, y) in [(5, 2), (6, 5), (3, 5)]:
        grid[y][x] = GridCell.CRYSTAL

    return Map(
        width=width,
        height=height,
        player_start_x=2,
        player_start_y=2,
        grid=tuple(tuple(row) for row in grid),
    )


MAP_DECOUVERTE: Final[Map] = _make_map_decouverte()
