import arcade
import random
from dataclasses import dataclass
import math

@dataclass
class BatInfo:
    sprite: arcade.Sprite
    # Bornes de déplacement de la chauve-souris
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    vx: float
    vy: float

def _norme(vx: float, vy: float) -> float:
    return math.sqrt(vx * vx + vy * vy)

def _renormalise(vx: float, vy: float, speed: float) -> tuple[float, float]:
    # garantie que la chauve-souris se déplace à la même vitesse dans toutes les directions
    norme = _norme(vx, vy)
    if norme == 0:
        return speed, 0.0
    return (vx / norme) * speed, (vy / norme) * speed

def update_bats(bats_info: list[BatInfo], rng: random.Random, speed: float = 2.0, turn_probability: float = 0.04,) -> None:
    for info in bats_info:
        # changement de direction aléatoire
        if rng.random() < turn_probability:
            info.vx += rng.uniform(-0.8, 0.8)
            info.vy += rng.uniform(-0.8, 0.8)
            info.vx, info.vy = _renormalise(info.vx, info.vy, speed)
        next_x = info.sprite.center_x + info.vx
        next_y = info.sprite.center_y + info.vy
        # rebond sur les murs
        if next_x < info.min_x or next_x > info.max_x:
            info.vx *= -1
        if next_y < info.min_y or next_y > info.max_y:
            info.vy *= -1
        info.vx, info.vy = _renormalise(info.vx, info.vy, speed)
        info.sprite.center_x += info.vx
        info.sprite.center_y += info.vy
