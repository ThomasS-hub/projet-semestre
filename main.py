import sys

import arcade

from constants import *
from gameview import GameView
from map import InvalidMapFileException, load_map_from_file


DEFAULT_MAP_PATH = "maps/map1.txt"


def main() -> None:
    filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MAP_PATH

    try:
        game_map = load_map_from_file(filename)
    except FileNotFoundError:
        print(f"Fichier introuvable : {filename}")
        return
    except InvalidMapFileException as e:
        print(f"Erreur dans le fichier de map : {e}")
        return

    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE)
    game_view = GameView(game_map)
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
