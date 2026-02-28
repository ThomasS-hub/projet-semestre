from pyglet.resource import animation
from arcade.key import F
from typing import Final
import arcade
from textures import *
from textures import SOUND_COIN



from constants import *

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

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


    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]


    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()
        self.player = arcade.TextureAnimationSprite(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE, center_x=grid_to_pixels(2), center_y=grid_to_pixels(2)
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList(use_spatial_hash=True)
        for x in range(40):
            for y in range(20):
                grass = arcade.Sprite(
                    TEXTURE_GRASS, scale=SCALE,
                    center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                )
                self.grounds.append(grass)
        for (x,y) in [(3,6), (7,2), (2,10),(3,8)]:
            bush = arcade.Sprite(
              TEXTURE_BUSH, scale=SCALE,
              center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
            )
            self.walls.append(bush)
        for (x, y) in [(5, 2), (6, 5), (3, 5)]:
            crystal = arcade.Sprite(scale=SCALE)
            crystal.textures = CRYSTAL_TEXTURES
            crystal.texture = CRYSTAL_TEXTURES[0]
            crystal.center_x = grid_to_pixels(x)
            crystal.center_y = grid_to_pixels(y)
            self.crystals.append(crystal)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = 40 * TILE_SIZE
        self.world_height = 20 * TILE_SIZE

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
         """Render the screen."""
         self.clear() # always start with self.clear()
         with self.camera.activate():
                self.grounds.draw()
                self.walls.draw()
                self.crystals.draw()
                self.player_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match symbol:
            case arcade.key.RIGHT:
                # start moving to the right
                self.player.change_x = +PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                # start moving upwards
                self.player.change_y = +PLAYER_MOVEMENT_SPEED
            case arcade.key.DOWN:
                # start moving downwards
                self.player.change_y = -PLAYER_MOVEMENT_SPEED
            case arcade.key.ESCAPE:
                self.window.show_view(GameView())

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match symbol:
            case arcade.key.RIGHT | arcade.key.LEFT:
                # stop horizontal movement
                self.player.change_x = 0
            case arcade.key.UP | arcade.key.DOWN:
                # stop vertical movement
                self.player.change_y = 0
    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()
        self.crystals.update_animation()
        self.player.update_animation()
        self.camera.position = self.player.position
        hit_list = arcade.check_for_collision_with_list(self.player, self.crystals)
        for crystal in hit_list:
            arcade.play_sound(SOUND_COIN)
            crystal.remove_from_sprite_lists()
