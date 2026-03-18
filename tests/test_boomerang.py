import math
from gameview import Boomerang, Direction, BoomerangState


def test_launch_sets_state_and_direction():
    b = Boomerang(0, 0)

    b.launch(100, 200, Direction.East)

    assert b.state == BoomerangState.LAUNCHING
    assert b.dx == 1
    assert b.dy == 0
    assert b.sprite.center_x == 100
    assert b.sprite.center_y == 200


def test_launch_does_nothing_if_active():
    b = Boomerang(0, 0)

    b.launch(0, 0, Direction.East)
    old_dx, old_dy = b.dx, b.dy

    b.launch(50, 50, Direction.North)

    # ne doit pas changer
    assert b.dx == old_dx
    assert b.dy == old_dy


def test_update_launching_moves_boomerang():
    b = Boomerang(0, 0)
    b.launch(0, 0, Direction.East)

    b.update_launching()

    assert b.sprite.center_x == b.speed
    assert b.sprite.center_y == 0


def test_distance_travelled_increases():
    b = Boomerang(0, 0)
    b.launch(0, 0, Direction.East)

    b.update_launching()

    assert b.distance_travelled == b.speed


def test_reached_max_distance():
    b = Boomerang(0, 0)
    b.launch(0, 0, Direction.East)

    b.distance_travelled = b.max_distance

    assert b.reached_max_distance()


def test_switch_to_returning():
    b = Boomerang(0, 0)

    b.switch_to_returning()

    assert b.state == BoomerangState.RETURNING


def test_update_returning_moves_towards_player():
    b = Boomerang(0, 0)
    b.sprite.center_x = 100
    b.sprite.center_y = 0

    b.state = BoomerangState.RETURNING

    b.update_returning(0, 0)

    assert b.sprite.center_x < 100  # il revient vers 0


def test_is_close_to_player():
    b = Boomerang(0, 0)

    b.sprite.center_x = 5
    b.sprite.center_y = 0
    b.speed = 10

    assert b.is_close_to_player(0, 0)


def test_deactivate_resets_state():
    b = Boomerang(0, 0)

    b.state = BoomerangState.RETURNING
    b.deactivate(50, 60)

    assert b.state == BoomerangState.INACTIVE
    assert b.sprite.center_x == 50
    assert b.sprite.center_y == 60


def test_rotation_changes_texture_index():
    b = Boomerang(0, 0)
    b.launch(0, 0, Direction.East)

    initial_index = b.sprite.cur_texture_index

    b.update_launching()

    assert b.sprite.cur_texture_index != initial_index
