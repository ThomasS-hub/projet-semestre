from dataclasses import dataclass
from enum import Enum
from typing import Final
import math
import networkx as nx
from constants import TILE_SIZE


class GridCell(Enum): # meme chose changer le enum car ce n'est pas un enum ici
    GRASS = 0
    BUSH = 1
    CRYSTAL = 2
    SPINNER_HORIZONTAL = 3
    SPINNER_VERTICAL = 4
    HOLE = 5
    BAT = 6
    SLIME = 7


@dataclass(frozen=True)
class Map:
    width: int
    height: int
    player_start_x: int
    player_start_y: int
    grid: tuple[tuple[GridCell, ...], ...]
    navmesh: nx.Graph[tuple[int, int]]

    def get_cell(self, x: int, y: int) -> GridCell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("Position hors de la map")
        return self.grid[self.height - 1 - y][x]


class InvalidMapFileException(Exception):
    pass


def build_navmesh(width: int, height: int, grid: tuple[tuple[GridCell, ...], ...]) -> nx.Graph[tuple[int, int]]: # construit un graphe de navigation à partir de la grille de la map, en connectant les cases adjacentes qui ne sont pas des buissons ou des trous, et en attribuant un poids égal à la distance entre les centres des cases (TILE_SIZE pour les cases orthogonales, sqrt(2)*TILE_SIZE pour les cases diagonales)
    graph: nx.Graph[tuple[int, int]] = nx.Graph()

    def get_cell(x: int, y: int) -> GridCell:
        return grid[height - 1 - y][x]

    for x in range(width):
        for y in range(height):
            cell = get_cell(x, y)
            if cell in {GridCell.BUSH, GridCell.HOLE}:
                continue

            graph.add_node((x, y))

    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    ] # directions de déplacement possibles (orthogonales et diagonales)

    for x in range(width):
        for y in range(height):
            if (x, y) not in graph:
                continue

            for dx, dy in directions:
                nx_, ny_ = x + dx, y + dy

                if nx_ < 0 or nx_ >= width or ny_ < 0 or ny_ >= height:
                    continue

                if (nx_, ny_) not in graph: # on relie seulement les cases qui sont dans le graphe, c'est à dire qui ne sont pas des buissons ou des trous
                    continue

                if dx == 0 or dy == 0:
                    weight = TILE_SIZE
                else:
                    weight = math.sqrt(2) * TILE_SIZE # distance entre les centres de deux cases diagonales

                graph.add_edge((x, y), (nx_, ny_), weight=weight) # on ajoute une arête entre les deux cases avec le poids correspondant à la distance entre leurs centres

    return graph


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
        "v": GridCell.BAT,
        "m": GridCell.SLIME,
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

    assert player_start_x is not None
    assert player_start_y is not None

    return Map(
        width=width,
        height=height,
        player_start_x = player_start_x,
        player_start_y = player_start_y,
        grid=tuple(grid_rows),
        navmesh=build_navmesh(width, height, tuple(grid_rows)),
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

    grid_tuples = tuple(tuple(row) for row in grid)

    return Map(
        width=width,
        height=height,
        player_start_x=2,
        player_start_y=2,
        grid=grid_tuples,
        navmesh=build_navmesh(width, height, grid_tuples),
    )


MAP_DECOUVERTE: Final[Map] = _make_map_decouverte()
