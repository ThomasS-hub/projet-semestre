import arcade
import random
import math
from dataclasses import dataclass
import networkx as nx
from map import Map, GridCell
from constants import TILE_SIZE

@dataclass
class SlimeInfo:
    sprite: arcade.Sprite
    start_x: int
    start_y: int
    possible_destinations: list[tuple[int, int]]
    current_path: list[tuple[int, int]]
    path_index: int
    speed: float

def grid_to_pixels(i: int, tile_size: int) -> float: # convertit une coordonnée de grille en coordonnée de pixel, en centrant sur la tile
    return (i * tile_size) + (tile_size / 2)

def slime_possible_destinations(game_map: Map, x: int, y: int, tile_size: int) -> list[tuple[int, int]]: # calcule toutes les destinations possibles du slime dans sa zone de patrouille ( un carré de 7x7 centré sur sa position de départ) en excluant les cases occupées par des buissons ou des trous
    destinations: list[tuple[int, int]] = []

    for dx in range(-3, 4):
        for dy in range(-3, 4):
            nx = x + dx
            ny = y + dy

            if nx < 0 or nx >= game_map.width or ny < 0 or ny >= game_map.height:
                continue

            cell = game_map.get_cell(nx, ny)

            if cell not in {GridCell.BUSH, GridCell.HOLE}:
                destinations.append((nx, ny))

    return destinations

def slime_current_node(info: SlimeInfo, tile_size: int) -> tuple[int, int]: # retourne la position actuelle du slime en coordonnées de grille
    return (int(info.sprite.center_x // tile_size), int(info.sprite.center_y // tile_size))

def choose_new_destination(info: SlimeInfo, rng: random.Random, game_map: Map) -> None:
    start = slime_current_node(info, TILE_SIZE)

    reachable = []

    for dest in info.possible_destinations:
        if dest in game_map.navmesh and nx.has_path(game_map.navmesh, start, dest):
            reachable.append(dest)

    if len(reachable) == 0:
        info.current_path = []
        info.path_index = 0
        return

    target = rng.choice(reachable)

    path = nx.shortest_path(
        game_map.navmesh,
        source=start,
        target=target,
        weight="weight"
    )

    info.current_path = path
    info.path_index = 1 if len(path) > 1 else 0


def update_slimes(slimes_info: list[SlimeInfo], rng: random.Random, game_map: Map, tile_size: int) -> None: # met à jour la position de chaque slime en se dirigeant vers sa destination, et choisit une nouvelle destination lorsque le slime atteint la précédente
    for info in slimes_info:

        if len(info.current_path) == 0 or info.path_index >= len(info.current_path):
            choose_new_destination(info, rng, game_map)

            if len(info.current_path) == 0:
                continue

        target_node = info.current_path[info.path_index]

        target_x = grid_to_pixels(target_node[0], tile_size)
        target_y = grid_to_pixels(target_node[1], tile_size)

        dx = target_x - info.sprite.center_x
        dy = target_y - info.sprite.center_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= info.speed:

            info.sprite.center_x = target_x
            info.sprite.center_y = target_y

            info.path_index += 1

            if info.path_index >= len(info.current_path):
                choose_new_destination(info, rng, game_map)
            continue
        info.sprite.center_x += (dx / distance) * info.speed
        info.sprite.center_y += (dy / distance) * info.speed
