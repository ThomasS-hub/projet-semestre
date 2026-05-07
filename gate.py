from dataclasses import dataclass
from typing import Any

import arcade

from textures import (
    TEXTURE_SWITCH_OFF,
    TEXTURE_SWITCH_ON,
    TEXTURE_GATE_OPEN,
    TEXTURE_GATE_CLOSED,
)

type GateCondition = dict[str, Any]


@dataclass
class SwitchInfo:
    id: str
    sprite: arcade.Sprite
    is_on: bool


@dataclass
class GateInfo:
    sprite: arcade.Sprite
    condition: GateCondition
    is_open: bool


def switch_states(switches_info: list[SwitchInfo]) -> dict[str, bool]:
    return {switch.id: switch.is_on for switch in switches_info}


def evaluate_condition(condition: GateCondition, states: dict[str, bool]) -> bool:
    if "switch_is_on" in condition:
        switch_id = condition["switch_is_on"]

        if switch_id not in states:
            raise ValueError(f"switch inconnu: {switch_id}")

        return states[switch_id]

    if "not" in condition:
        return not evaluate_condition(condition["not"], states)

    if "and" in condition:
        return all(evaluate_condition(c, states) for c in condition["and"])

    if "or" in condition:
        return any(evaluate_condition(c, states) for c in condition["or"])

    raise ValueError(f"Condition invalide: {condition}")


def update_switch_texture(switch: SwitchInfo) -> None:
    switch.sprite.texture = TEXTURE_SWITCH_ON if switch.is_on else TEXTURE_SWITCH_OFF


def update_gate_state(gate: GateInfo, states: dict[str, bool], walls: arcade.SpriteList) -> None:
    gate.is_open = evaluate_condition(gate.condition, states)

    if gate.is_open:
        gate.sprite.texture = TEXTURE_GATE_OPEN
        if gate.sprite in walls:
            walls.remove(gate.sprite)
    else:
        gate.sprite.texture = TEXTURE_GATE_CLOSED
        if gate.sprite not in walls:
            walls.append(gate.sprite)


def update_all_gates(
    gates_info: list[GateInfo],
    switches_info: list[SwitchInfo],
    walls: arcade.SpriteList,
) -> None:
    states = switch_states(switches_info)

    for gate in gates_info:
        update_gate_state(gate, states, walls)
