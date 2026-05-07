import pytest

from map import (
    GridCell,
    Map,
    InvalidMapFileException,
    load_map_from_string,
    build_navmesh,
)


def test_get_cell_basic() -> None:
    grid = (
        (GridCell.BUSH, GridCell.CRYSTAL, GridCell.GRASS),
        (GridCell.HOLE, GridCell.SPINNER_HORIZONTAL, GridCell.SPINNER_VERTICAL),
    )

    game_map = Map(
        width=3,
        height=2,
        player_start_x=0,
        player_start_y=0,
        grid=grid,
        navmesh=build_navmesh(3, 2, grid),
        switches=(),
        gates=(),
    )

    assert game_map.get_cell(0, 0) == GridCell.HOLE
    assert game_map.get_cell(1, 0) == GridCell.SPINNER_HORIZONTAL
    assert game_map.get_cell(2, 0) == GridCell.SPINNER_VERTICAL
    assert game_map.get_cell(0, 1) == GridCell.BUSH
    assert game_map.get_cell(1, 1) == GridCell.CRYSTAL
    assert game_map.get_cell(2, 1) == GridCell.GRASS


def test_get_cell_out_of_bounds() -> None:
    grid = (
        (GridCell.GRASS, GridCell.GRASS),
        (GridCell.GRASS, GridCell.GRASS),
    )

    game_map = Map(
        width=2,
        height=2,
        player_start_x=0,
        player_start_y=0,
        grid=grid,
        navmesh=build_navmesh(2, 2, grid),
        switches=(),
        gates=(),
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

    assert game_map.switches == ()
    assert game_map.gates == ()


def test_load_map_with_switch_and_gate() -> None:
    content = """width: 8
height: 4
switches:
  - id: first
    x: 3
    y: 1
    state: off
gates:
  - x: 5
    y: 1
    open_if:
      switch_is_on: first
---
xxxxxxxx
x      x
x P^ | x
xxxxxxxx
---
"""

    game_map = load_map_from_string(content)

    assert len(game_map.switches) == 1
    assert game_map.switches[0].id == "first"
    assert game_map.switches[0].x == 3
    assert game_map.switches[0].y == 1
    assert game_map.switches[0].is_on is False

    assert len(game_map.gates) == 1
    assert game_map.gates[0].x == 5
    assert game_map.gates[0].y == 1
    assert game_map.gates[0].open_if == {"switch_is_on": "first"}


def test_load_map_with_switch_initially_on() -> None:
    content = """width: 6
height: 4
switches:
  - id: first
    x: 3
    y: 1
    state: on
---
xxxxxx
x    x
x P^ x
xxxxxx
---
"""

    game_map = load_map_from_string(content)

    assert len(game_map.switches) == 1
    assert game_map.switches[0].is_on is True


def test_switch_config_must_match_grid_symbol() -> None:
    content = """width: 6
height: 4
switches:
  - id: first
    x: 3
    y: 1
    state: off
---
xxxxxx
x    x
x P  x
xxxxxx
---
"""

    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_gate_config_must_match_grid_symbol() -> None:
    content = """width: 6
height: 4
gates:
  - x: 3
    y: 1
    open_if:
      switch_is_on: first
---
xxxxxx
x    x
x P  x
xxxxxx
---
"""

    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


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


def test_build_navmesh_excludes_bush_hole_and_gate() -> None:
    width = 3
    height = 3
    grid = [
        [GridCell.GRASS, GridCell.GRASS, GridCell.GRASS],
        [GridCell.GRASS, GridCell.BUSH, GridCell.GATE],
        [GridCell.GRASS, GridCell.HOLE, GridCell.GRASS],
    ]
    grid_tuple = tuple(tuple(row) for row in grid)

    navmesh = build_navmesh(width, height, grid_tuple)

    assert all(node[0:2] != (1, 1) for node in navmesh)
    assert all(node[0:2] != (1, 0) for node in navmesh)
    assert all(node[0:2] != (2, 1) for node in navmesh)
    assert any(node[0:2] == (0, 0) for node in navmesh)
    assert any(node[0:2] == (2, 2) for node in navmesh)

def test_load_map_with_switches() -> None:
    content = """width: 5
height: 3
switches:
  - id: a
    x: 1
    y: 1
    state: on
---
xxxxx
x^P x
xxxxx
---
"""

    game_map = load_map_from_string(content)

    assert len(game_map.switches) == 1
    s = game_map.switches[0]

    assert s.id == "a"
    assert s.x == 1
    assert s.y == 1
    assert s.is_on is True

def test_load_map_with_switches() -> None:
    content = """width: 5
height: 3
switches:
  - id: a
    x: 1
    y: 1
    state: on
---
xxxxx
x^P x
xxxxx
---
"""

    game_map = load_map_from_string(content)

    assert len(game_map.switches) == 1
    s = game_map.switches[0]

    assert s.id == "a"
    assert s.x == 1
    assert s.y == 1
    assert s.is_on is True

def test_switch_position_mismatch() -> None:
    content = """width: 3
height: 3
switches:
  - id: a
    x: 1
    y: 1
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)

def test_gate_position_mismatch() -> None:
    content = """width: 3
height: 3
gates:
  - x: 1
    y: 1
    open_if:
      switch_is_on: a
---
xxx
xPx
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)
