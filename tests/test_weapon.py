import arcade
import pytest

from constants import SCALE, TILE_SIZE
from gameview import Weapon, WeaponType, WeaponState, Direction, GameView, grid_to_pixels
from map import MAP_DECOUVERTE


@pytest.fixture
def view():
    window = arcade.Window(800, 600, visible=False)
    game_view = GameView(MAP_DECOUVERTE)
    window.show_view(game_view)
    yield game_view
    window.close()


def test_weapon_initial_state() -> None:
    weapon = Weapon(100, 200)

    assert weapon.weapon_type == WeaponType.BOOMERANG
    assert weapon.state == WeaponState.INACTIVE
    assert weapon.is_active() is False


def test_change_weapon_type_to_epee() -> None:
    weapon = Weapon(0, 0)

    weapon.change_weapon_type()

    assert weapon.weapon_type == WeaponType.EPEE
    assert weapon.state == WeaponState.INACTIVE


def test_change_weapon_type_back_to_boomerang() -> None:
    weapon = Weapon(0, 0)

    weapon.change_weapon_type()
    weapon.change_weapon_type()

    assert weapon.weapon_type == WeaponType.BOOMERANG
    assert weapon.state == WeaponState.INACTIVE


def test_cannot_change_weapon_type_when_active() -> None:
    weapon = Weapon(0, 0)
    weapon.use_boomerang(0, 0, Direction.East)

    weapon.change_weapon_type()

    assert weapon.weapon_type == WeaponType.BOOMERANG
    assert weapon.state == WeaponState.LAUNCHING


def test_set_scale_boomerang() -> None:
    weapon = Weapon(0, 0)
    weapon.set_weapon_type(WeaponType.BOOMERANG)

    assert weapon.sprite.scale == (SCALE, SCALE)


def test_set_scale_epee() -> None:
    weapon = Weapon(0, 0)
    weapon.set_weapon_type(WeaponType.EPEE)

    assert weapon.sprite.scale == (1.3, 1.3)


def test_use_boomerang_sets_launching_state() -> None:
    weapon = Weapon(50, 50)

    weapon.use(50, 50, Direction.North)

    assert weapon.state == WeaponState.LAUNCHING
    assert weapon.distance_travelled == 0.0


def test_use_boomerang_sets_direction_vector() -> None:
    weapon = Weapon(0, 0)

    weapon.use_boomerang(0, 0, Direction.West)

    assert weapon.dx == -1
    assert weapon.dy == 0


def test_update_launching_moves_boomerang() -> None:
    weapon = Weapon(100, 100)
    weapon.use_boomerang(100, 100, Direction.East)

    old_x = weapon.sprite.center_x
    old_y = weapon.sprite.center_y

    weapon.update_launching()

    assert weapon.sprite.center_x == old_x + weapon.speed
    assert weapon.sprite.center_y == old_y
    assert weapon.distance_travelled == weapon.speed


def test_reached_max_distance() -> None:
    weapon = Weapon(0, 0)
    weapon.distance_travelled = weapon.max_distance

    assert weapon.reached_max_distance() is True


def test_switch_to_returning() -> None:
    weapon = Weapon(0, 0)

    weapon.switch_to_returning()

    assert weapon.state == WeaponState.RETURNING


def test_update_returning_moves_toward_player() -> None:
    weapon = Weapon(100, 100)
    weapon.state = WeaponState.RETURNING
    weapon.sprite.center_x = 50
    weapon.sprite.center_y = 100

    weapon.update_returning(100, 100)

    assert weapon.sprite.center_x > 50
    assert weapon.sprite.center_y == 100


def test_is_close_to_player_true() -> None:
    weapon = Weapon(0, 0)
    weapon.sprite.center_x = 5
    weapon.sprite.center_y = 0
    weapon.speed = 8

    assert weapon.is_close_to_player(0, 0) is True


def test_deactivate_sets_inactive_and_moves_sprite() -> None:
    weapon = Weapon(0, 0)
    weapon.state = WeaponState.RETURNING

    weapon.deactivate(10, 20)

    assert weapon.state == WeaponState.INACTIVE
    assert weapon.sprite.center_x == 10
    assert weapon.sprite.center_y == 20


def test_use_epee_sets_active_state() -> None:
    weapon = Weapon(100, 100)
    weapon.set_weapon_type(WeaponType.EPEE)

    weapon.use(100, 100, Direction.South)

    assert weapon.weapon_type == WeaponType.EPEE
    assert weapon.state == WeaponState.ACTIVE
    assert weapon.time == 0.0


def test_use_epee_places_sprite_north() -> None:
    weapon = Weapon(100, 100)
    weapon.set_weapon_type(WeaponType.EPEE)

    weapon.use_epee(100, 100, Direction.North)

    assert weapon.sprite.center_x == 100
    assert weapon.sprite.center_y == 100 + int(1.25 * TILE_SIZE)


def test_use_epee_places_sprite_east() -> None:
    weapon = Weapon(100, 100)
    weapon.set_weapon_type(WeaponType.EPEE)

    weapon.use_epee(100, 100, Direction.East)

    assert weapon.sprite.center_x == 100 + int(1.25 * TILE_SIZE)
    assert weapon.sprite.center_y == 100


def test_update_epee_keeps_active_before_end() -> None:
    weapon = Weapon(0, 0)
    weapon.set_weapon_type(WeaponType.EPEE)
    weapon.use_epee(0, 0, Direction.South)

    weapon.update_epee(0.05)

    assert weapon.state == WeaponState.ACTIVE
    assert weapon.sprite.cur_texture_index == 1


def test_update_epee_becomes_inactive_after_animation() -> None:
    weapon = Weapon(0, 0)
    weapon.set_weapon_type(WeaponType.EPEE)
    weapon.use_epee(0, 0, Direction.South)

    weapon.update_epee(1.0)

    assert weapon.state == WeaponState.INACTIVE


def test_use_does_nothing_if_weapon_already_active() -> None:
    weapon = Weapon(0, 0)
    weapon.use_boomerang(0, 0, Direction.East)

    x_before = weapon.sprite.center_x
    y_before = weapon.sprite.center_y
    state_before = weapon.state

    weapon.use(200, 300, Direction.North)

    assert weapon.state == state_before
    assert weapon.sprite.center_x == x_before
    assert weapon.sprite.center_y == y_before


def test_update_weapon_icon_boomerang(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.BOOMERANG)

    view.update_weapon_icon()

    assert view.weapon_icon.texture is not None


def test_update_weapon_icon_epee(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.EPEE)

    view.update_weapon_icon()

    assert view.weapon_icon.texture is not None


def test_boomerang_hits_bush_true(view: GameView) -> None:
    bush_x = 3
    bush_y = 6
    view.weapon.sprite.center_x = grid_to_pixels(bush_x)
    view.weapon.sprite.center_y = grid_to_pixels(bush_y)

    assert view.boomerang_hits_bush() is True


def test_boomerang_hits_bush_false(view: GameView) -> None:
    view.weapon.sprite.center_x = grid_to_pixels(0)
    view.weapon.sprite.center_y = grid_to_pixels(0)

    assert view.boomerang_hits_bush() is False


def test_check_boomerang_hits_spinners_removes_spinner(view: GameView) -> None:
    spinner = arcade.Sprite(center_x=200, center_y=200)
    view.spinners.append(spinner)
    view.spinners_info.append(
        type(
            "FakeSpinnerInfo",
            (),
            {
                "sprite": spinner,
                "horizontal": True,
                "min_pos": 0,
                "max_pos": 0,
                "speed": 0,
            },
        )()
    )

    view.weapon.sprite.center_x = 200
    view.weapon.sprite.center_y = 200

    result = view.check_boomerang_hits_spinners()

    assert result is True
    assert spinner not in view.spinners


def test_check_epee_hits_removes_spinner(view: GameView, monkeypatch) -> None:
    monkeypatch.setattr(arcade, "play_sound", lambda *_args, **_kwargs: None)

    spinner = arcade.Sprite(center_x=150, center_y=150)
    view.spinners.append(spinner)
    view.spinners_info.append(
        type(
            "FakeSpinnerInfo",
            (),
            {
                "sprite": spinner,
                "horizontal": True,
                "min_pos": 0,
                "max_pos": 0,
                "speed": 0,
            },
        )()
    )

    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.sprite.center_x = 150
    view.weapon.sprite.center_y = 150

    view.check_epee_hits()

    assert spinner not in view.spinners


def test_check_epee_hits_collects_crystal(view: GameView, monkeypatch) -> None:
    monkeypatch.setattr(arcade, "play_sound", lambda *_args, **_kwargs: None)

    crystal = arcade.Sprite(center_x=180, center_y=180)
    view.crystals.append(crystal)
    score_before = view.score

    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.sprite.center_x = 180
    view.weapon.sprite.center_y = 180

    view.check_epee_hits()

    assert crystal not in view.crystals
    assert view.score == score_before + 1


def test_on_key_press_r_changes_weapon_when_inactive(view: GameView) -> None:
    view.on_key_press(arcade.key.R, 0)

    assert view.weapon.weapon_type == WeaponType.EPEE


def test_on_key_press_r_does_nothing_when_weapon_active(view: GameView) -> None:
    view.weapon.use_boomerang(view.player.center_x, view.player.center_y, Direction.East)

    view.on_key_press(arcade.key.R, 0)

    assert view.weapon.weapon_type == WeaponType.BOOMERANG


def test_on_key_press_d_uses_current_weapon(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.EPEE)

    view.on_key_press(arcade.key.D, 0)

    assert view.weapon.state == WeaponState.ACTIVE


def test_on_key_press_blocks_movement_when_epee_active(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.use_epee(view.player.center_x, view.player.center_y, Direction.North)

    view.on_key_press(arcade.key.RIGHT, 0)

    assert view.player.change_x == 0
    assert view.player.change_y == 0


def test_on_key_release_blocks_movement_when_epee_active(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.use_epee(view.player.center_x, view.player.center_y, Direction.North)

    view.player.change_x = 5
    view.player.change_y = 7

    view.on_key_release(arcade.key.RIGHT, 0)

    assert view.player.change_x == 5
    assert view.player.change_y == 7
