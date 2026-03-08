import pytest

from map import GridCell, InvalidMapFileException, load_map_from_string


def test_load_valid_map():
    content = """width: 4
height: 3
---
x  P
 **
x
---
"""
    m = load_map_from_string(content)

    assert m.width == 4
    assert m.height == 3
    assert m.player_start_x == 3
    assert m.player_start_y == 2


def test_missing_player():
    content = """width: 3
height: 2
---
xxx
***
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_two_players():
    content = """width: 3
height: 2
---
P P
xxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_invalid_character():
    content = """width: 3
height: 1
---
aP
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_line_too_long():
    content = """width: 3
height: 1
---
xxxx
---
"""
    with pytest.raises(InvalidMapFileException):
        load_map_from_string(content)


def test_get_cell_coordinates():
    content = """width: 2
height: 2
---
xP
 *
---
"""
    m = load_map_from_string(content)

    assert m.get_cell(0, 1) == GridCell.BUSH
    assert m.get_cell(1, 0) == GridCell.CRYSTAL
