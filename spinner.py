from dataclasses import dataclass
import arcade
from map import Map, GridCell

@dataclass
class SpinnerInfo:
    sprite: arcade.Sprite
    horizontal: bool
    min_pos: int
    max_pos: int
    speed: int

def spinner_horizontal_limits(game_map: Map, x: int, y: int) -> tuple[int, int]:
    left = x
    while left - 1 >= 0 and game_map.get_cell(left - 1, y) != GridCell.BUSH:
        left -= 1

    right = x
    while right + 1 < game_map.width and game_map.get_cell(right + 1, y) != GridCell.BUSH:
        right += 1

    return left, right


def spinner_vertical_limits(game_map: Map, x: int, y: int) -> tuple[int, int]:
    down = y
    while down - 1 >= 0 and game_map.get_cell(x, down - 1) != GridCell.BUSH:
        down -= 1

    up = y
    while up + 1 < game_map.height and game_map.get_cell(x, up + 1) != GridCell.BUSH:
        up += 1

    return down, up

def update_spinners(spinners_info: list[SpinnerInfo]) -> None:
    for info in spinners_info:
            if info.horizontal:
                info.sprite.center_x += info.speed

                if info.sprite.center_x >= info.max_pos:
                    info.sprite.center_x = info.max_pos
                    info.speed *= -1
                elif info.sprite.center_x <= info.min_pos:
                    info.sprite.center_x = info.min_pos
                    info.speed *= -1
            else:
                info.sprite.center_y += info.speed

                if info.sprite.center_y >= info.max_pos:
                    info.sprite.center_y = info.max_pos
                    info.speed *= -1
                elif info.sprite.center_y <= info.min_pos:
                    info.sprite.center_y = info.min_pos
                    info.speed *= -1
