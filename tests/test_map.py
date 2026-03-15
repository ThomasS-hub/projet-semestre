import pytest

from map import (
    GridCell,
    Map,
    InvalidMapFileException,
    load_map_from_string,
)


def test_get_cell_basic() -> None:
    game_map = Map(
        width=3,
        height=2,
        player_start_x=0,
        player_start_y=0,
        grid=(
            (GridCell.BUSH, GridCell.CRYSTAL, GridCell.GRASS),
            (GridCell.HOLE, GridCell.SPINNER_HORIZONTAL, GridCell.SPINNER_VERTICAL),
        ),
    )

    assert game_map.get_cell(0, 0) == GridCell.HOLE
    assert game_map.get_cell(1, 0) == GridCell.SPINNER_HORIZONTAL
    assert game_map.get_cell(2, 0) == GridCell.SPINNER_VERTICAL
    assert game_map.get_cell(0, 1) == GridCell.BUSH
    assert game_map.get_cell(1, 1) == GridCell.CRYSTAL
    assert game_map.get_cell(2, 1) == GridCell.GRASS


def test_get_cell_out_of_bounds() -> None:
    game_map = Map(
        width=2,
        height=2,
        player_start_x=0,
        player_start_y=0,
        grid=(
            (GridCell.GRASS, GridCell.GRASS),
            (GridCell.GRASS, GridCell.GRASS),
        ),
    )

    with pytest.raises(IndexError):
        game_map.get_cell(-1, 0)

    with pytest.raises(IndexError):
        game_map.get_cell(0, -1)

    with pytest.raises(IndexError):
        game_map.get_cell(2, 0)

    with pytest.raises(IndexError):
        game_map.get_cell(0, 2)


def test_load_map_from_string_valid() -> None:
    content = """width: 5
height: 4
---
xxxxx
xP *x
xsSOx
xxxxx
---
"""

    game_map = load_map_from_string(content)

    assert game_map.width == 5
    assert game_map.height == 4
    assert game_map.player_start_x == 1
    assert game_map.player_start_y == 2

    assert game_map.get_cell(0, 3) == GridCell.BUSH
    assert game_map.get_cell(2, 2) == GridCell.GRASS
    assert game_map.get_cell(3, 2) == GridCell.CRYSTAL
    assert game_map.get_cell(1, 1) == GridCell.SPINNER_HORIZONTAL
    assert game_map.get_cell(2, 1) == GridCell.SPINNER_VERTICAL
    assert game_map.get_cell(3, 1) == GridCell.HOLE


def test_load_map_requires_exactly_one_player() -> None:
    content_no_player = """width: 3
height: 3
---
xxx
x x
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content_no_player)

    content_two_players = """width: 3
height: 3
---
xPx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content_two_players)


def test_load_map_invalid_character() -> None:
    content = """width: 3
height: 3
---
xxx
xPx
xAx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_missing_width() -> None:
    content = """height: 3
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_missing_height() -> None:
    content = """width: 3
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_invalid_width() -> None:
    content = """width: -3
height: 3
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_invalid_height() -> None:
    content = """width: 3
height: 0
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_missing_start_separator() -> None:
    content = """width: 3
height: 3
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_missing_end_separator() -> None:
    content = """width: 3
height: 3
---
xxx
xPx
xxx
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_line_too_long() -> None:
    content = """width: 3
height: 3
---
xxxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_load_map_short_lines_are_padded_with_grass() -> None:
    content = """width: 5
height: 3
---
xxxxx
xP
xxxxx
---
"""
    game_map = load_map_from_string(content)

    assert game_map.get_cell(2, 1) == GridCell.GRASS
    assert game_map.get_cell(3, 1) == GridCell.GRASS
    assert game_map.get_cell(4, 1) == GridCell.GRASS
