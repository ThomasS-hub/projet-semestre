import arcade
import random
import math
from dataclasses import dataclass
import networkx as nx
from map import Map, GridCell, NavNode
from constants import TILE_SIZE
from player import Player

@dataclass
class SlimeInfo:
    sprite: arcade.Sprite
    start_x: int
    start_y: int
    possible_destinations: list[NavNode]
    current_path: list[NavNode]
    path_index: int
    speed: float
    target_node: NavNode | None

def node_to_pixels(node: NavNode, tile_size: int) -> tuple[float, float]: # convertit une position de noeud du graphe de navigation en coordonnées de pixels pour déplacer le sprite du slime
    x, y, sx, sy = node
    density = 3

    px = x * tile_size + ((2 * sx + 1) * tile_size) / (2 * density)
    py = y * tile_size + ((2 * sy + 1) * tile_size) / (2 * density)

    return px, py

def closest_navmesh_node(game_map: Map, x: float, y: float) -> NavNode | None: # trouve le noeud du graphe de navigation le plus proche d'une position donnée (en pixels) pour initialiser la position du slime sur le navmesh
    best_node: NavNode | None = None
    best_distance = float("inf")

    for node in game_map.navmesh.nodes:
        px, py = node_to_pixels(node, TILE_SIZE)

        dx = px - x
        dy = py - y
        distance = dx * dx + dy * dy

        if distance < best_distance:
            best_distance = distance
            best_node = node

    return best_node

def slime_possible_destinations(game_map: Map, x: int, y: int, tile_size: int) -> list[NavNode]: # calcule toutes les destinations possibles du slime dans sa zone de patrouille ( un carré de 7x7 centré sur sa position de départ) en excluant les cases occupées par des buissons ou des trous
    destinations: list[NavNode] = []
    for node in game_map.navmesh.nodes:
        node_x, node_y, _, _ = node
        if abs(node_x - x) <= 3 and abs(node_y - y) <= 3:
            destinations.append(node)
    return destinations

def slime_current_node(info: SlimeInfo, game_map: Map) -> NavNode | None:
    return closest_navmesh_node(game_map,info.sprite.center_x,info.sprite.center_y)

def choose_new_destination(info: SlimeInfo, rng: random.Random, game_map: Map) -> None:
    start = slime_current_node(info, game_map)
    if start is None:
        info.current_path = []
        info.path_index = 0
        return

    reachable = []

    for dest in info.possible_destinations:
        if (start in game_map.navmesh and dest in game_map.navmesh and nx.has_path(game_map.navmesh, start, dest)):
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
    info.target_node = None

def slime_can_see_player(info: SlimeInfo, player: Player, walls: arcade.SpriteList, max_distance: float) -> bool: # vérifie si le slime peut voir le joueur en traçant une ligne entre les deux et en vérifiant si elle intersecte une tile de buisson
    dx = player.center_x - info.sprite.center_x
    dy = player.center_y - info.sprite.center_y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance > max_distance:
        return False
    return arcade.has_line_of_sight((info.sprite.center_x, info.sprite.center_y), (player.center_x, player.center_y), walls) # utilise la fonction d'arcade pour vérifier la ligne de vue entre le slime et le joueur, en tenant compte des murs (buissons) qui pourraient bloquer la vue

def slime_chase_player(info: SlimeInfo, game_map: Map, target: NavNode, tile_size: int) -> None: # met à jour la position du slime pour qu'il se dirige vers le joueur en utilisant le navmesh pour trouver le chemin le plus court
     start = slime_current_node(info, game_map)
     if start is None:
        info.current_path = []
        info.path_index = 0
        return

     if target not in game_map.navmesh:
        info.current_path = []
        info.path_index = 0
        return

     if not nx.has_path(game_map.navmesh, start, target):
        info.current_path = []
        info.path_index = 0
        return

     path = nx.shortest_path(game_map.navmesh,source=start,target=target,weight="weight")
     info.current_path = path
     info.path_index = 1 if len(path) > 1 else 0
     info.target_node = target



def update_slimes(slimes_info: list[SlimeInfo], rng: random.Random, game_map: Map, tile_size: int, player: Player, walls: arcade.SpriteList) -> None: # met à jour la position de chaque slime en se dirigeant vers sa destination, et choisit une nouvelle destination lorsque le slime atteint la précédente
    for info in slimes_info:
        player_node = closest_navmesh_node(game_map, player.center_x, player.center_y)
        if player_node is None:
            continue
        player_cell_x, player_cell_y, _, _ = player_node
        player_inside_zone = (abs(player_cell_x - info.start_x) <= 3 and abs(player_cell_y - info.start_y) <= 3) # vérifie si le joueur est dans la zone de patrouille du slime (un carré de 7x7 centré sur sa position de départ)

        if player_inside_zone and slime_can_see_player(info, player, walls, max_distance=5 * tile_size):
            if info.target_node != player_node:
                slime_chase_player(info, game_map, player_node, tile_size)
        elif info.target_node is not None:
            info.target_node = None
            info.current_path = []
            info.path_index = 0

        if len(info.current_path) == 0 or info.path_index >= len(info.current_path):
            choose_new_destination(info, rng, game_map)

            if len(info.current_path) == 0:
                continue

        target_node = info.current_path[info.path_index]

        target_x, target_y = node_to_pixels(target_node, tile_size)

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
