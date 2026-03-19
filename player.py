import arcade
from enum import IntEnum

from constants import SCALE, PLAYER_MOVEMENT_SPEED
from textures import (
    ANIMATION_PLAYER_IDLE_DOWN,
    ANIMATION_PLAYER_IDLE_UP,
    ANIMATION_PLAYER_IDLE_LEFT,
    ANIMATION_PLAYER_IDLE_RIGHT,
    ANIMATION_PLAYER_RUN_DOWN,
    ANIMATION_PLAYER_RUN_UP,
    ANIMATION_PLAYER_RUN_LEFT,
    ANIMATION_PLAYER_RUN_RIGHT,
)

class Direction(IntEnum):
    North = 0
    South = 1
    West = 2
    East = 3

    def to_vector(self) -> tuple[int, int]: # permet d'extraire un vecteur déplacement d'une direction
        if self == Direction.East:
             return 1, 0
        if self == Direction.West:
            return -1, 0
        if self == Direction.North:
            return 0, 1
        return 0, -1

class Player(arcade.TextureAnimationSprite):
    direction: Direction

    def __init__(self) -> None:
        super().__init__(animation=ANIMATION_PLAYER_IDLE_DOWN, scale=SCALE)
        self.direction = Direction.South
        self.idle_animations = [
            ANIMATION_PLAYER_IDLE_UP,
            ANIMATION_PLAYER_IDLE_DOWN,
            ANIMATION_PLAYER_IDLE_LEFT,
            ANIMATION_PLAYER_IDLE_RIGHT,
        ]
        self.run_animations = [
            ANIMATION_PLAYER_RUN_UP,
            ANIMATION_PLAYER_RUN_DOWN,
            ANIMATION_PLAYER_RUN_LEFT,
            ANIMATION_PLAYER_RUN_RIGHT,
        ]
        self.animation = self.idle_animations[self.direction]
        self.texture = self.animation.keyframes[0].texture

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.change_x = PLAYER_MOVEMENT_SPEED
                self.direction = Direction.East
            case arcade.key.LEFT:
                self.change_x = -PLAYER_MOVEMENT_SPEED
                self.direction = Direction.West
            case arcade.key.UP:
                self.change_y = PLAYER_MOVEMENT_SPEED
                self.direction = Direction.North
            case arcade.key.DOWN:
                self.change_y = -PLAYER_MOVEMENT_SPEED
                self.direction = Direction.South
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.change_x = 0
            case arcade.key.LEFT:
                self.change_x = 0
            case arcade.key.UP:
                self.change_y = 0
            case arcade.key.DOWN:
                self.change_y = 0

    def update_animation_state(self, delta_time: float) -> None:
        if self.change_x == 0 and self.change_y == 0:
            self.animation = self.idle_animations[self.direction]
        else:
            self.animation = self.run_animations[self.direction]

        super().update_animation(delta_time)
