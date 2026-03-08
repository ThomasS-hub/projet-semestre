from pyglet.resource import animation
from arcade.key import F
from typing import Final
import arcade
from textures import *
from textures import SOUND_COIN
from map import Map, GridCell
from dataclasses import dataclass



from constants import *

LEFT_MARGIN = 200
RIGHT_MARGIN = 200
BOTTOM_MARGIN = 200
TOP_MARGIN = 200

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

@dataclass
class SpinnerInfo:
    sprite: arcade.Sprite
    horizontal: bool
    min_pos: int
    max_pos: int
    speed: int

class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    player: Final[arcade.TextureAnimationSprite]
    player_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    grounds: Final[arcade.SpriteList]
    walls: Final[arcade.SpriteList]
    crystals: Final[arcade.SpriteList]
    keys_down: set[int]
    spinners: Final[arcade.SpriteList]
    spinners_info: list[SpinnerInfo]


    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]


    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()
        self.map = map
        self.player = arcade.TextureAnimationSprite(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE, center_x=grid_to_pixels(map.player_start_x), center_y=grid_to_pixels(map.player_start_y)
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList(use_spatial_hash=True)
        self.spinners = arcade.SpriteList()
        self.spinners_info = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                cell = self.map.get_cell(x, y)
                grass = arcade.Sprite(
                    TEXTURE_GRASS, scale=SCALE,
                    center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                )
                self.grounds.append(grass)
                if cell == GridCell.BUSH:
                    bush = arcade.Sprite(
                        TEXTURE_BUSH, scale=SCALE,
                        center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                    )
                    self.walls.append(bush)
                elif cell == GridCell.CRYSTAL:
                    crystal = arcade.Sprite(scale=SCALE)
                    crystal.textures = CRYSTAL_TEXTURES
                    crystal.texture = CRYSTAL_TEXTURES[0]
                    crystal.center_x = grid_to_pixels(x)
                    crystal.center_y = grid_to_pixels(y)
                    self.crystals.append(crystal)
                elif cell == GridCell.SPINNER_HORIZONTAL:
                    spinner = arcade.Sprite(scale=SCALE)
                    spinner.textures = SPINNER_TEXTURES
                    spinner.texture = SPINNER_TEXTURES[0]
                    spinner.center_x = grid_to_pixels(x)
                    spinner.center_y = grid_to_pixels(y)
                    self.spinners.append(spinner)
                    min_x, max_x = self._spinner_horizontal_limits(x, y)
                    self.spinners_info.append(
                        SpinnerInfo(
                            sprite=spinner,
                            horizontal=True,
                            min_pos=grid_to_pixels(min_x),
                            max_pos=grid_to_pixels(max_x),
                            speed=3,
                        )
                    )
                elif cell == GridCell.SPINNER_VERTICAL:
                    spinner = arcade.Sprite(scale=SCALE)
                    spinner.textures = SPINNER_TEXTURES
                    spinner.texture = SPINNER_TEXTURES[0]
                    spinner.center_x = grid_to_pixels(x)
                    spinner.center_y = grid_to_pixels(y)
                    self.spinners.append(spinner)
                    min_y, max_y = self._spinner_vertical_limits(x, y)
                    self.spinners_info.append(
                        SpinnerInfo(
                            sprite=spinner,
                            horizontal=False,
                            min_pos=grid_to_pixels(min_y),
                            max_pos=grid_to_pixels(max_y),
                            speed=3,
                        )
                    )

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def _spinner_horizontal_limits(self, x: int, y: int) -> tuple[int, int]:
        left = x
        while left - 1 >= 0 and self.map.get_cell(left - 1, y) != GridCell.BUSH:
            left -= 1

        right = x
        while right + 1 < self.map.width and self.map.get_cell(right + 1, y) != GridCell.BUSH:
            right += 1

        return left, right


    def _spinner_vertical_limits(self, x: int, y: int) -> tuple[int, int]:
        down = y
        while down - 1 >= 0 and self.map.get_cell(x, down - 1) != GridCell.BUSH:
            down -= 1

        up = y
        while up + 1 < self.map.height and self.map.get_cell(x, up + 1) != GridCell.BUSH:
            up += 1

        return down, up

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)
        w = self.window.width
        h = self.window.height

        cx = min(max(self.player.center_x, w/2), self.world_width - w/2)
        cy = min(max(self.player.center_y, h/2), self.world_height - h/2)

        self.camera.position = (cx, cy)

    def on_draw(self) -> None:
         """Render the screen."""
         self.clear() # always start with self.clear()
         with self.camera.activate():
                self.grounds.draw()
                self.walls.draw()
                self.crystals.draw()
                self.spinners.draw()
                self.player_list.draw()


    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.right_pressed = True
            case arcade.key.LEFT:
                self.left_pressed = True
            case arcade.key.UP:
                self.up_pressed = True
            case arcade.key.DOWN:
                self.down_pressed = True
            case arcade.key.ESCAPE:
                self.window.show_view(GameView())

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.right_pressed = False
            case arcade.key.LEFT:
                self.left_pressed = False
            case arcade.key.UP:
                self.up_pressed = False
            case arcade.key.DOWN:
                self.down_pressed = False

    def _update_camera(self) -> None:
        cam_cx, cam_cy = self.camera.position  # CENTRE
        w = self.window.width
        h = self.window.height

        # Convertir en coin bas-gauche du viewport
        cam_left = cam_cx - w / 2
        cam_bottom = cam_cy - h / 2

        left_boundary = cam_left + LEFT_MARGIN
        right_boundary = cam_left + w - RIGHT_MARGIN
        bottom_boundary = cam_bottom + BOTTOM_MARGIN
        top_boundary = cam_bottom + h - TOP_MARGIN

        # X
        if self.player.left < left_boundary:
            cam_left = self.player.left - LEFT_MARGIN
        elif self.player.right > right_boundary:
            cam_left = self.player.right - (w - RIGHT_MARGIN)

        # Y
        if self.player.bottom < bottom_boundary:
            cam_bottom = self.player.bottom - BOTTOM_MARGIN
        elif self.player.top > top_boundary:
            cam_bottom = self.player.top - (h - TOP_MARGIN)

        # Clamp sur le coin bas-gauche
        max_left = max(0, self.world_width - w)
        max_bottom = max(0, self.world_height - h)

        cam_left = min(max(cam_left, 0), max_left)
        cam_bottom = min(max(cam_bottom, 0), max_bottom)

        # Reconvertir en CENTRE
        self.camera.position = (cam_left + w / 2, cam_bottom + h / 2)

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.player.change_x = PLAYER_MOVEMENT_SPEED * (self.right_pressed - self.left_pressed)
        self.player.change_y = PLAYER_MOVEMENT_SPEED * (self.up_pressed - self.down_pressed)
        self.physics_engine.update()
        self.crystals.update_animation()
        self.player.update_animation()
        self._update_camera()
        hit_list = arcade.check_for_collision_with_list(self.player, self.crystals)
        for crystal in hit_list:
            arcade.play_sound(SOUND_COIN)
            crystal.remove_from_sprite_lists()
        self.spinners.update()
        for info in self.spinners_info:
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

        self.spinners.update_animation()

        if arcade.check_for_collision_with_list(self.player, self.spinners):
            self.window.show_view(GameView(self.map))
            return
