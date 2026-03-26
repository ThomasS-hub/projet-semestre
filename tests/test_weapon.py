import arcade
import pytest

from constants import SCALE, TILE_SIZE
from weapon import Weapon, WeaponType, WeaponState
from player import Direction
from gameview import GameView, grid_to_pixels, SpinnerInfo, BatInfo
from map import MAP_DECOUVERTE
from pytest import MonkeyPatch
from collections.abc import Generator


@pytest.fixture
def view() -> Generator[GameView, None, None]:
    window = arcade.Window(800, 600, visible=False)
    game_view = GameView(MAP_DECOUVERTE)
    window.show_view(game_view)
    yield game_view
    window.close()


# =========================
# WEAPON TESTS
# =========================

def test_weapon_initial_state() -> None:
    weapon = Weapon(100, 200)

    assert weapon.weapon_type == WeaponType.BOOMERANG
    assert weapon.state == WeaponState.INACTIVE
    assert weapon.is_active() is False


def test_change_weapon_type() -> None:
    weapon = Weapon(0, 0)

    weapon.change_weapon_type()
    assert weapon.weapon_type == WeaponType.EPEE

    weapon.change_weapon_type()
    assert weapon.weapon_type == WeaponType.BOOMERANG


def test_cannot_change_weapon_type_when_active() -> None:
    weapon = Weapon(0, 0)
    weapon.use_boomerang(0, 0, Direction.East)

    weapon.change_weapon_type()

    assert weapon.weapon_type == WeaponType.BOOMERANG
    assert weapon.state == WeaponState.LAUNCHING


def test_set_scale() -> None:
    weapon = Weapon(0, 0)

    weapon.set_weapon_type(WeaponType.BOOMERANG)
    assert weapon.sprite.scale == (SCALE, SCALE)

    weapon.set_weapon_type(WeaponType.EPEE)
    assert weapon.sprite.scale == (1.3, 1.3)


def test_boomerang_launch() -> None:
    weapon = Weapon(50, 50)

    weapon.use(50, 50, Direction.North)

    assert weapon.state == WeaponState.LAUNCHING
    assert weapon.distance_travelled == 0.0


def test_direction_vector() -> None:
    weapon = Weapon(0, 0)

    weapon.use_boomerang(0, 0, Direction.West)

    assert weapon.dx == -1
    assert weapon.dy == 0


def test_update_launching() -> None:
    weapon = Weapon(100, 100)
    weapon.use_boomerang(100, 100, Direction.East)

    old_x = weapon.sprite.center_x

    weapon.update_launching()

    assert weapon.sprite.center_x == old_x + weapon.speed
    assert weapon.distance_travelled == weapon.speed


def test_reached_max_distance() -> None:
    weapon = Weapon(0, 0)
    weapon.distance_travelled = weapon.max_distance

    assert weapon.reached_max_distance() is True


def test_returning() -> None:
    weapon = Weapon(100, 100)
    weapon.state = WeaponState.RETURNING
    weapon.sprite.center_x = 50

    weapon.update_returning(100, 100)

    assert weapon.sprite.center_x > 50


def test_deactivate() -> None:
    weapon = Weapon(0, 0)
    weapon.state = WeaponState.RETURNING

    weapon.deactivate(10, 20)

    assert weapon.state == WeaponState.INACTIVE
    assert weapon.sprite.center_x == 10


def test_epee_activation() -> None:
    weapon = Weapon(100, 100)
    weapon.set_weapon_type(WeaponType.EPEE)

    weapon.use(100, 100, Direction.South)

    assert weapon.state == WeaponState.ACTIVE


def test_epee_position() -> None:
    weapon = Weapon(100, 100)
    weapon.set_weapon_type(WeaponType.EPEE)

    weapon.use_epee(100, 100, Direction.East)

    assert weapon.sprite.center_x == 100 + int(1.25 * TILE_SIZE)


def test_update_epee() -> None:
    weapon = Weapon(0, 0)
    weapon.set_weapon_type(WeaponType.EPEE)
    weapon.use_epee(0, 0, Direction.South)

    weapon.update_epee(1.0)

    assert weapon.state == WeaponState.INACTIVE


# =========================
# GAMEVIEW TESTS
# =========================

def test_weapon_icon(view: GameView) -> None:
    view.weapon.set_weapon_type(WeaponType.BOOMERANG)

    view.update_weapon_icon()

    assert view.weapon_icon.texture is not None


def test_boomerang_hits_bush_true(view: GameView) -> None:
    view.weapon.sprite.center_x = grid_to_pixels(3)
    view.weapon.sprite.center_y = grid_to_pixels(6)

    assert view.boomerang_hits_bush() is True


def test_boomerang_hits_bush_false(view: GameView) -> None:
    view.weapon.sprite.center_x = grid_to_pixels(0)
    view.weapon.sprite.center_y = grid_to_pixels(0)

    assert view.boomerang_hits_bush() is False


def test_boomerang_hits_monster(view: GameView) -> None:
    spinner = arcade.Sprite(center_x=200, center_y=200)
    view.spinners.append(spinner)
    view.spinners_info.append(
        SpinnerInfo(
            sprite=spinner,
            horizontal=True,
            min_pos=0,
            max_pos=1000,
            speed=3,
        )
    )


    view.weapon.sprite.center_x = 200
    view.weapon.sprite.center_y = 200

    result = view.check_boomerang_hits_monsters()

    assert result is True
    assert spinner not in view.spinners


def test_epee_hits_monster(view: GameView, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(arcade, "play_sound", lambda *_: None)

    bat = arcade.Sprite(center_x=150, center_y=150)
    view.bats.append(bat)
    view.bats_info.append(
        BatInfo(
            sprite=bat,
            min_x=0,
            max_x=1000,
            min_y=0,
            max_y=1000,
            vx=2.0,
            vy=0.0,
        )
    )


    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.sprite.center_x = 150
    view.weapon.sprite.center_y = 150

    view.check_epee_hits()

    assert bat not in view.bats


def test_epee_hits_crystal(view: GameView, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(arcade, "play_sound", lambda *_: None)

    crystal = arcade.Sprite(center_x=180, center_y=180)
    view.crystals.append(crystal)
    score_before = view.score

    view.weapon.set_weapon_type(WeaponType.EPEE)
    view.weapon.sprite.center_x = 180
    view.weapon.sprite.center_y = 180

    view.check_epee_hits()

    assert crystal not in view.crystals
    assert view.score == score_before + 1
