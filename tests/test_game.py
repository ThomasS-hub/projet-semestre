import arcade

from gameview import GameView, grid_to_pixels
from player import Direction
from map import load_map_from_string
from spinner import spinner_horizontal_limits, spinner_vertical_limits


def make_view_from_string(content: str) -> GameView:
    game_map = load_map_from_string(content)
    return GameView(game_map)


def test_view_initializes_collections(window: arcade.Window) -> None:
    content = """width: 6
height: 5
---
xxxxxx
x *  x
x sO x
x P  x
xxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    assert len(view.grounds) == 6 * 5
    assert len(view.walls) == 18
    assert len(view.crystals) == 1
    assert len(view.spinners) == 1
    assert len(view.holes) == 1
    assert view.score == 0


def test_player_starts_at_correct_position(window: arcade.Window) -> None:
    content = """width: 5
height: 5
---
xxxxx
x   x
x P x
x   x
xxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    assert view.player.center_x == grid_to_pixels(2)
    assert view.player.center_y == grid_to_pixels(2)


def test_player_moves_right(window: arcade.Window) -> None:
    content = """width: 6
height: 5
---
xxxxxx
x    x
x P  x
x    x
xxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    start_x = view.player.center_x

    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(10)

    assert view.player.center_x > start_x
    assert view.player.direction == Direction.East


def test_player_stops_after_key_release(window: arcade.Window) -> None:
    content = """width: 6
height: 5
---
xxxxxx
x    x
x P  x
x    x
xxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(5)
    view.on_key_release(arcade.key.RIGHT, 0)

    x_after_release = view.player.center_x
    window.test(5)

    assert view.player.center_x == x_after_release


def test_collect_crystal_and_score_updates(window: arcade.Window) -> None:
    content = """width: 7
height: 5
---
xxxxxxx
x     x
x P*  x
x     x
xxxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    assert len(view.crystals) == 1
    assert view.score == 0

    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(20)

    assert len(view.crystals) == 0
    assert view.score == 1
    assert view.score_text.text == "Score: 1"


def test_player_falls_into_hole(window: arcade.Window) -> None:
    content = """width: 7
height: 5
---
xxxxxxx
x     x
x PO  x
x     x
xxxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    old_view = window.current_view
    assert old_view is view

    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(20)

    assert window.current_view is not old_view
    assert isinstance(window.current_view, GameView)
    assert window.current_view.score == 0


def test_spinner_horizontal_limits(window: arcade.Window) -> None:
    content = """width: 9
height: 5
---
xxxxxxxxx
x       x
x xs  x x
x   P   x
xxxxxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    left, right = spinner_horizontal_limits(view.map, 2, 2)
    assert left == 1
    assert right == 5


def test_spinner_vertical_limits(window: arcade.Window) -> None:
    content = """width: 7
height: 7
---
xxxxxxx
x  x  x
x  S  x
x     x
x     x
x  xPx
xxxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    down, up = spinner_vertical_limits(view.map, 3, 4)
    assert down == 2
    assert up == 4


def test_spinner_collision_resets_game(window: arcade.Window) -> None:
    content = """width: 8
height: 5
---
xxxxxxxx
x      x
x Ps   x
x      x
xxxxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    old_view = window.current_view

    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(20)

    assert window.current_view is not old_view
    assert isinstance(window.current_view, GameView)


def test_direction_changes_with_input(window: arcade.Window) -> None:
    content = """width: 6
height: 5
---
xxxxxx
x    x
x P  x
x    x
xxxxxx
---
"""
    view = make_view_from_string(content)
    window.show_view(view)

    view.on_key_press(arcade.key.UP, 0)
    assert view.player.direction == Direction.North

    view.on_key_press(arcade.key.LEFT, 0)
    assert view.player.direction == Direction.West

    view.on_key_press(arcade.key.DOWN, 0)
    assert view.player.direction == Direction.South

    view.on_key_press(arcade.key.RIGHT, 0)
    assert view.player.direction == Direction.East
    assert view.player.direction == Direction.East
