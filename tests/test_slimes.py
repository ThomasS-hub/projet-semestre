import arcade
import random

from map import Map, GridCell, build_navmesh
from slimes import SlimeInfo, slime_possible_destinations, choose_new_destination, update_slimes
from constants import TILE_SIZE
from player import Player


def make_map(
    width: int = 7,
    height: int = 7,
    blocked: list[tuple[int, int, GridCell]] | None = None,
) -> Map:
    grid = [[GridCell.GRASS for _ in range(width)] for _ in range(height)]

    if blocked is not None:
        for x, y, cell in blocked:
            grid[height - 1 - y][x] = cell

    grid_tuple = tuple(tuple(row) for row in grid)

    return Map(
        width=width,
        height=height,
        player_start_x=0,
        player_start_y=0,
        grid=grid_tuple,
        navmesh=build_navmesh(width, height, grid_tuple),
    )


def make_sprite(x: int, y: int) -> arcade.Sprite:
    sprite = arcade.Sprite()
    sprite.center_x = x * TILE_SIZE + TILE_SIZE / 2
    sprite.center_y = y * TILE_SIZE + TILE_SIZE / 2
    return sprite

def make_player_far_away() -> Player:
    player = Player()
    player.center_x = 1000
    player.center_y = 1000
    return player

def make_empty_walls() -> arcade.SpriteList:
    return arcade.SpriteList()


def test_slime_possible_destinations_excludes_bush_and_hole() -> None:
    game_map = make_map(
        blocked=[
            (1, 1, GridCell.BUSH),
            (3, 3, GridCell.HOLE),
        ]
    )

    destinations = slime_possible_destinations(game_map, 2, 2, TILE_SIZE)

    assert all(node[0:2] != (1, 1) for node in destinations)
    assert all(node[0:2] != (3, 3) for node in destinations)
    assert any(node[0:2] == (2, 2) for node in destinations)
    assert any(node[0:2] == (0, 0) for node in destinations)
    assert any(node[0:2] == (4, 4) for node in destinations)


def test_choose_new_destination_builds_a_path() -> None:
    game_map = make_map(
        blocked=[
            (2, 2, GridCell.BUSH),
        ]
    )

    sprite = make_sprite(1, 1)
    info = SlimeInfo(
        sprite=sprite,
        start_x=1,
        start_y=1,
        possible_destinations=[(3, 3, 1, 1)],
        current_path=[],
        path_index=0,
        speed=1.0,
        target_node=None,
    )

    choose_new_destination(info, random.Random(0), game_map)

    assert len(info.current_path) > 0
    assert info.current_path[0][0:2] == (1, 1)
    assert info.current_path[-1][0:2] == (3, 3)
    assert all(node[0:2] != (2, 2) for node in info.current_path)


def test_update_slimes_moves_towards_next_node() -> None:
    game_map = make_map()

    sprite = make_sprite(1, 1)
    info = SlimeInfo(
        sprite=sprite,
        start_x=1,
        start_y=1,
        possible_destinations=[(2, 1, 1, 1)],
        current_path=[(1, 1, 1, 1), (2, 1, 1, 1)],
        path_index=1,
        speed=1.0,
        target_node=None,
    )

    old_x = sprite.center_x
    old_y = sprite.center_y

    update_slimes([info], random.Random(0), game_map, TILE_SIZE, make_player_far_away(), make_empty_walls())

    assert sprite.center_x > old_x
    assert sprite.center_y == old_y


def test_update_slimes_advances_path_index_when_reaching_node() -> None:
    game_map = make_map()

    sprite = make_sprite(1, 1)
    target_x = 2 * TILE_SIZE + TILE_SIZE / 2
    target_y = 1 * TILE_SIZE + TILE_SIZE / 2

    sprite.center_x = target_x - 0.5
    sprite.center_y = target_y

    info = SlimeInfo(
        sprite=sprite,
        start_x=1,
        start_y=1,
        possible_destinations=[(2, 1, 1, 1), (3, 1, 1, 1)],
        current_path=[(1, 1, 1, 1), (2, 1, 1, 1), (3, 1, 1, 1)],
        path_index=1,
        speed=1.0,
        target_node=None,
    )

    update_slimes([info], random.Random(0), game_map, TILE_SIZE, make_player_far_away(), make_empty_walls())

    assert sprite.center_x == target_x
    assert sprite.center_y == target_y
    assert info.path_index == 2


def test_update_slimes_chooses_new_path_when_finished() -> None:
    game_map = make_map()

    sprite = make_sprite(2, 1)

    info = SlimeInfo(
        sprite=sprite,
        start_x=2,
        start_y=1,
        possible_destinations=[(3, 1, 1, 1)],
        current_path=[],
        path_index=0,
        speed=1.0,
        target_node=None,
    )

    update_slimes([info], random.Random(0), game_map, TILE_SIZE, make_player_far_away(), make_empty_walls())

    assert len(info.current_path) > 0
    assert info.current_path[0][0:2] == (2, 1)
    assert info.current_path[-1][0:2] == (3, 1)

def test_slime_pursues_player_when_visible() -> None:
    game_map = make_map()
    player = Player()
    player.center_x = 3 * TILE_SIZE + TILE_SIZE / 2
    player.center_y = 1 * TILE_SIZE + TILE_SIZE / 2
    sprite = make_sprite(1, 1)

    info = SlimeInfo(
        sprite=sprite,
        start_x=1,
        start_y=1,
        possible_destinations=[(2, 1, 1, 1)],
        current_path=[],
        path_index=0,
        speed=1.0,
        target_node=None,
    )
    update_slimes(
        [info],
        random.Random(0),
        game_map,
        TILE_SIZE,
        player,
        arcade.SpriteList(),
    )
    assert info.target_node is not None
    assert info.target_node[0:2] == (3, 1)
    assert len(info.current_path) > 0
