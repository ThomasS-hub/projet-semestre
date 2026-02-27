from typing import Final
import arcade

ORIG_TILE_SIZE = (16, 16)

def _load_grid(
    file: str,
    columns: int,
    rows: int,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE
) -> list[arcade.Texture]:
    """
    Loads a texture grid from a spritesheet.

    Args:
        file:
            Path to the spritesheet file name.
        columns:
            The number of columns in the grid.
        rows:
            The number of rows in the grid.
        tile_size (optional):
            The size in pixels of one element of the grid. Defaults to the
            standard tile size of `(16, 16)` that we use in our assets.

    Returns:
        A list of the loaded textures, flattened by row. The texture at grid
        coordinates `(x, y)` is at index `(y * columns) + x` in the list.
    """
    spritesheet = arcade.load_spritesheet(file)
    return spritesheet.get_texture_grid(tile_size, columns, columns * rows)

_overworld_grid = _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Overworld_Tileset.png", 18, 13)

TEXTURE_GRASS: Final[arcade.Texture] = _overworld_grid[18*1 + 6]
TEXTURE_BUSH: Final[arcade.Texture] = _overworld_grid[18*3 + 5]

TEXTURE_PLAYER_IDLE_DOWN: Final[arcade.Texture] = \
    _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_down_anim_strip_6.png", 1, 1)[0]
