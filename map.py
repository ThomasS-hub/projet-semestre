from arcade.key import O
from dataclasses import dataclass
from enum import Enum
from typing import Final


class GridCell(Enum):
    GRASS = 0
    BUSH = 1
    CRYSTAL = 2
    SPINNER_HORIZONTAL = 3
    SPINNER_VERTICAL = 4
    HOLE = 5
    BAT = 6


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
        return self.grid[self.height - 1 - y][x]


class InvalidMapFileException(Exception):
    pass


def load_map_from_file(filename: str) -> Map:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return load_map_from_string(content)


def load_map_from_string(content: str) -> Map:
    lines = content.splitlines()

    if len(lines) < 4:
        raise InvalidMapFileException("fichier trop court")

    width = None
    height = None
    i = 0

    while i < len(lines) and lines[i] != "---":
        line = lines[i].strip()

        if ":" not in line:
            raise InvalidMapFileException("ligne de configuration invalide")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "width":
            if not value.isdigit() or int(value) <= 0:
                raise InvalidMapFileException("width invalide")
            width = int(value)

        elif key == "height":
            if not value.isdigit() or int(value) <= 0:
                raise InvalidMapFileException("height invalide")
            height = int(value)

        else:
            raise InvalidMapFileException(f"clé inconnue: {key}")

        i += 1

    if width is None or height is None:
        raise InvalidMapFileException("width ou height manquant")

    if i >= len(lines) or lines[i] != "---":
        raise InvalidMapFileException("séparateur de début manquant")

    i += 1

    if i + height > len(lines):
        raise InvalidMapFileException("pas assez de lignes pour la carte")

    map_lines = lines[i:i + height]
    i += height

    if i >= len(lines) or lines[i] != "---":
        raise InvalidMapFileException("séparateur de fin manquant")

    allowed = {
        " ": GridCell.GRASS,
        "x": GridCell.BUSH,
        "*": GridCell.CRYSTAL,
        "s": GridCell.SPINNER_HORIZONTAL,
        "S": GridCell.SPINNER_VERTICAL,
        "O": GridCell.HOLE,
        "V": GridCell.BAT,
    }

    player_start_x = None
    player_start_y = None
    player_count = 0
    grid_rows: list[tuple[GridCell, ...]] = []

    for file_row_index, raw_line in enumerate(map_lines):
        if len(raw_line) > width:
            raise InvalidMapFileException("ligne trop longue")

        padded_line = raw_line.ljust(width)
        row: list[GridCell] = []

        for x, ch in enumerate(padded_line):
            if ch == "P":
                player_count += 1
                player_start_x = x
                player_start_y = height - 1 - file_row_index
                row.append(GridCell.GRASS)
            elif ch in allowed:
                row.append(allowed[ch])
            else:
                raise InvalidMapFileException(f"caractère invalide: {ch}")

        grid_rows.append(tuple(row))

    if player_count != 1:
        raise InvalidMapFileException("il faut exactement un P")

    return Map(
        width=width,
        height=height,
        player_start_x=player_start_x,
        player_start_y=player_start_y,
        grid=tuple(grid_rows),
    )


def _make_map_decouverte() -> Map:
    width = 40
    height = 20

    grid = [[GridCell.GRASS for _ in range(width)] for _ in range(height)]

    for (x, y) in [(3, 6), (7, 2), (2, 10), (3, 8)]:
        grid[height - 1 - y][x] = GridCell.BUSH

    for (x, y) in [(5, 2), (6, 5), (3, 5)]:
        grid[height - 1 - y][x] = GridCell.CRYSTAL

    for (x, y) in [(10, 5), (15, 8)]:
        grid[height - 1 - y][x] = GridCell.SPINNER_HORIZONTAL

    for (x, y) in [(20, 10), (25, 4)]:
        grid[height - 1 - y][x] = GridCell.SPINNER_VERTICAL

    for (x,y) in [(8,8),(9,8),(15,5),(10,4),(13,2),(4,10)]:
        grid[height - 1 - y][x] = GridCell.HOLE

    return Map(
        width=width,
        height=height,
        player_start_x=2,
        player_start_y=2,
        grid=tuple(tuple(row) for row in grid),
    )


MAP_DECOUVERTE: Final[Map] = _make_map_decouverte()
