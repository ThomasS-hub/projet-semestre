import arcade
import random

from map import Map, GridCell, build_navmesh
from slimes import SlimeInfo, slime_possible_destinations, choose_new_destination, update_slimes
from constants import TILE_SIZE


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


def test_slime_possible_destinations_excludes_bush_and_hole() -> None:
    game_map = make_map(
        blocked=[
            (1, 1, GridCell.BUSH),
            (3, 3, GridCell.HOLE),
        ]
    )

    destinations = slime_possible_destinations(game_map, 2, 2, TILE_SIZE)

    assert (1, 1) not in destinations
    assert (3, 3) not in destinations
    assert (2, 2) in destinations
    assert (0, 0) in destinations
    assert (4, 4) in destinations


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
        possible_destinations=[(3, 3)],
        current_path=[],
        path_index=0,
        speed=1.0,
    )

    choose_new_destination(info, random.Random(0), game_map)

    assert len(info.current_path) > 0
    assert info.current_path[0] == (1, 1)
    assert info.current_path[-1] == (3, 3)
    assert (2, 2) not in info.current_path


def test_update_slimes_moves_towards_next_node() -> None:
    game_map = make_map()

    sprite = make_sprite(1, 1)
    info = SlimeInfo(
        sprite=sprite,
        start_x=1,
        start_y=1,
        possible_destinations=[(2, 1)],
        current_path=[(1, 1), (2, 1)],
        path_index=1,
        speed=1.0,
    )

    old_x = sprite.center_x
    old_y = sprite.center_y

    update_slimes([info], random.Random(0), game_map, TILE_SIZE)

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
        possible_destinations=[(2, 1), (3, 1)],
        current_path=[(1, 1), (2, 1), (3, 1)],
        path_index=1,
        speed=1.0,
    )

    update_slimes([info], random.Random(0), game_map, TILE_SIZE)

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
        possible_destinations=[(3, 1)],
        current_path=[],
        path_index=0,
        speed=1.0,
    )

    update_slimes([info], random.Random(0), game_map, TILE_SIZE)

    assert len(info.current_path) > 0
    assert info.current_path[0] == (2, 1)
    assert info.current_path[-1] == (3, 1)
