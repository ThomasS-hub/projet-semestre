from typing import Final
import arcade
from textures import *


from constants import *

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()
        self.player = arcade.Sprite(
            TEXTURE_PLAYER_IDLE_DOWN,
            scale=SCALE, center_x=grid_to_pixels(2), center_y=grid_to_pixels(2)
        )

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
         arcade.draw_sprite(self.player)
         arcade.draw_sprite(self.player)
