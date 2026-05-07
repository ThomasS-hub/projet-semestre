import arcade
import pytest

from gate import (
    GateInfo,
    SwitchInfo,
    evaluate_condition,
    switch_states,
    update_all_gates,
)


def test_evaluate_switch_is_on() -> None:
    states = {"first": True}

    assert evaluate_condition({"switch_is_on": "first"}, states) is True


def test_evaluate_not() -> None:
    states = {"first": False}

    condition = {
        "not": {
            "switch_is_on": "first",
        }
    }

    assert evaluate_condition(condition, states) is True


def test_evaluate_and() -> None:
    states = {"first": True, "second": False}

    condition = {
        "and": [
            {"switch_is_on": "first"},
            {
                "not": {
                    "switch_is_on": "second",
                }
            },
        ]
    }

    assert evaluate_condition(condition, states) is True


def test_evaluate_or() -> None:
    states = {"first": False, "second": True}

    condition = {
        "or": [
            {"switch_is_on": "first"},
            {"switch_is_on": "second"},
        ]
    }

    assert evaluate_condition(condition, states) is True


def test_unknown_switch_raises_value_error() -> None:
    with pytest.raises(ValueError):
        evaluate_condition({"switch_is_on": "missing"}, {"first": True})


def test_switch_states() -> None:
    sprite = arcade.Sprite()

    switches = [
        SwitchInfo(id="first", sprite=sprite, is_on=True),
        SwitchInfo(id="second", sprite=sprite, is_on=False),
    ]

    assert switch_states(switches) == {
        "first": True,
        "second": False,
    }


def test_update_all_gates_removes_open_gate_from_walls() -> None:
    switch_sprite = arcade.Sprite()
    gate_sprite = arcade.Sprite()

    walls = arcade.SpriteList()
    walls.append(gate_sprite)

    switches = [
        SwitchInfo(id="first", sprite=switch_sprite, is_on=True),
    ]

    gates = [
        GateInfo(
            sprite=gate_sprite,
            condition={"switch_is_on": "first"},
            is_open=False,
        )
    ]

    update_all_gates(gates, switches, walls)

    assert gates[0].is_open is True
    assert gate_sprite not in walls


def test_update_all_gates_adds_closed_gate_to_walls() -> None:
    switch_sprite = arcade.Sprite()
    gate_sprite = arcade.Sprite()

    walls = arcade.SpriteList()

    switches = [
        SwitchInfo(id="first", sprite=switch_sprite, is_on=False),
    ]

    gates = [
        GateInfo(
            sprite=gate_sprite,
            condition={"switch_is_on": "first"},
            is_open=True,
        )
    ]

    update_all_gates(gates, switches, walls)

    assert gates[0].is_open is False
    assert gate_sprite in walls
