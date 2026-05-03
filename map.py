from dataclasses import dataclass
from enum import Enum
from typing import Final
import math
import networkx as nx
from constants import TILE_SIZE

type NavNode = tuple[int, int, int, int] # type pour représenter une position de grille dans le graphe de navigation


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
    navmesh: nx.Graph[NavNode]

    def get_cell(self, x: int, y: int) -> GridCell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("Position hors de la map")
        return self.grid[self.height - 1 - y][x]


class InvalidMapFileException(Exception):
    pass


def build_navmesh(width: int,height: int,grid: tuple[tuple[GridCell, ...], ...],density: int = 3,) -> nx.Graph[NavNode]:
    graph: nx.Graph[NavNode] = nx.Graph()

    def get_cell(x: int, y: int) -> GridCell:
        return grid[height - 1 - y][x]

    def node_position(x: int, y: int, sx: int, sy: int) -> tuple[float, float]:
        px = x * TILE_SIZE + ((2 * sx + 1) * TILE_SIZE) / (2 * density)
        py = y * TILE_SIZE + ((2 * sy + 1) * TILE_SIZE) / (2 * density)
        return px, py

    def too_close_to_bush(px: float, py: float) -> bool:
        for bx in range(width):
            for by in range(height):
                if get_cell(bx, by) != GridCell.BUSH:
                    continue

                bush_x = bx * TILE_SIZE + TILE_SIZE / 2
                bush_y = by * TILE_SIZE + TILE_SIZE / 2

                dx = px - bush_x
                dy = py - bush_y

                if math.sqrt(dx * dx + dy * dy) < TILE_SIZE:
                    return True

        return False

    nodes_by_position: dict[tuple[int, int], NavNode] = {} # dictionnaire pour retrouver le noeud du graphe à partir d'une position globale (en comptant les subdivisions)

    for x in range(width):
        for y in range(height):
            if get_cell(x, y) in {GridCell.BUSH, GridCell.HOLE}:
                continue

            for sx in range(density):
                for sy in range(density):
                    px, py = node_position(x, y, sx, sy)

                    if too_close_to_bush(px, py):
                        continue

                    node = (x, y, sx, sy)
                    graph.add_node(node)

                    global_x = x * density + sx
                    global_y = y * density + sy
                    nodes_by_position[(global_x, global_y)] = node

    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    ]

    step = TILE_SIZE / density

    for (global_x, global_y), node in nodes_by_position.items(): # pour chaque noeud du graphe, on regarde les 8 positions globales autour de lui (en comptant les subdivisions) et si elles correspondent à un autre noeud du graphe, on ajoute une arête entre les deux
        for dx, dy in directions:
            other_position = (global_x + dx, global_y + dy)

            if other_position not in nodes_by_position:
                continue

            other_node = nodes_by_position[other_position]

            if dx == 0 or dy == 0:
                weight = step
            else:
                weight = math.sqrt(2) * step

            graph.add_edge(node, other_node, weight=weight)

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
