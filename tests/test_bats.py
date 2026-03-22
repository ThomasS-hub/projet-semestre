import math
import random
import arcade

from bats import BatInfo, _norme, _renormalise, update_bats


def test_norme() -> None:
    assert _norme(3, 4) == 5


def test_renormalise_garde_la_norme_voulue() -> None:
    vx, vy = _renormalise(3, 4, 2.0)
    assert math.isclose(_norme(vx, vy), 2.0)


def test_renormalise_vecteur_nul() -> None:
    vx, vy = _renormalise(0.0, 0.0, 2.0)
    assert vx == 2.0
    assert vy == 0.0


def test_update_bat_avance_en_ligne_droite_sans_aleatoire() -> None:
    bat = arcade.Sprite()
    bat.center_x = 50.0
    bat.center_y = 60.0
    info = BatInfo(
        sprite=bat,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=2.0,
        vy=0.0,
    )

    update_bats([info], random.Random(0), speed=2.0, turn_probability=0.0)

    assert math.isclose(bat.center_x, 52.0)
    assert math.isclose(bat.center_y, 60.0)
    assert math.isclose(info.vx, 2.0)
    assert math.isclose(info.vy, 0.0)


def test_update_bat_rebondit_sur_bord_droit() -> None:
    bat = arcade.Sprite()
    bat.center_x = 100.0
    bat.center_y = 50.0
    info = BatInfo(
        sprite=bat,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=2.0,
        vy=0.0,
    )

    update_bats([info], random.Random(0), speed=2.0, turn_probability=0.0)

    assert math.isclose(info.vx, -2.0)
    assert math.isclose(info.vy, 0.0)
    assert math.isclose(bat.center_x, 98.0)
    assert math.isclose(bat.center_y, 50.0)


def test_update_bat_rebondit_sur_bord_haut() -> None:
    bat = arcade.Sprite()
    bat.center_x = 40.0
    bat.center_y = 100.0
    info = BatInfo(
        sprite=bat,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=0.0,
        vy=2.0,
    )

    update_bats([info], random.Random(0), speed=2.0, turn_probability=0.0)

    assert math.isclose(info.vx, 0.0)
    assert math.isclose(info.vy, -2.0)
    assert math.isclose(bat.center_x, 40.0)
    assert math.isclose(bat.center_y, 98.0)


def test_update_bat_reste_dans_son_champ_action() -> None:
    bat = arcade.Sprite()
    bat.center_x = 50.0
    bat.center_y = 50.0
    info = BatInfo(
        sprite=bat,
        min_x=40,
        max_x=60,
        min_y=40,
        max_y=60,
        vx=2.0,
        vy=0.0,
    )

    rng = random.Random(0)
    for _ in range(50):
        update_bats([info], rng, speed=2.0, turn_probability=0.0)
        assert info.min_x <= bat.center_x <= info.max_x
        assert info.min_y <= bat.center_y <= info.max_y


def test_update_bat_garde_vitesse_constante() -> None:
    bat = arcade.Sprite()
    bat.center_x = 50.0
    bat.center_y = 50.0
    info = BatInfo(
        sprite=bat,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=2.0,
        vy=0.0,
    )

    rng = random.Random(123)
    for _ in range(20):
        update_bats([info], rng, speed=2.0, turn_probability=1.0)
        assert math.isclose(_norme(info.vx, info.vy), 2.0, rel_tol=1e-9, abs_tol=1e-9)


def test_update_bat_deterministe_avec_seed() -> None:
    bat1 = arcade.Sprite()
    bat1.center_x = 50.0
    bat1.center_y = 50.0
    info1 = BatInfo(
        sprite=bat1,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=2.0,
        vy=0.0,
    )

    bat2 = arcade.Sprite()
    bat2.center_x = 50.0
    bat2.center_y = 50.0
    info2 = BatInfo(
        sprite=bat2,
        min_x=0,
        max_x=100,
        min_y=0,
        max_y=100,
        vx=2.0,
        vy=0.0,
    )

    rng1 = random.Random(42)
    rng2 = random.Random(42)

    for _ in range(15):
        update_bats([info1], rng1, speed=2.0, turn_probability=0.3)
        update_bats([info2], rng2, speed=2.0, turn_probability=0.3)

    assert math.isclose(bat1.center_x, bat2.center_x)
    assert math.isclose(bat1.center_y, bat2.center_y)
    assert math.isclose(info1.vx, info2.vx)
    assert math.isclose(info1.vy, info2.vy)
