from typing import Final
import math
import arcade
import random

from constants import (
    TILE_SIZE,
    SCALE,
    MAX_WINDOW_WIDTH,
    MAX_WINDOW_HEIGHT,
)
from textures import (
    TEXTURE_GRASS,
    TEXTURE_BUSH,
    TEXTURE_HOLE,
    CRYSTAL_TEXTURES,
    SPINNER_TEXTURES,
    WEAPON_ICON_BOOMERANG,
    WEAPON_ICON_EPEE,
    SOUND_COIN,
    BAT_TEXTURES,
)
from map import Map, GridCell
from player import Player
from weapon import Weapon, WeaponType, WeaponState
from spinner import SpinnerInfo, spinner_horizontal_limits, spinner_vertical_limits, update_spinners
from camera import update_camera
from bats import BatInfo, update_bats

LEFT_MARGIN = 200
RIGHT_MARGIN = 200
BOTTOM_MARGIN = 200
TOP_MARGIN = 200

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    player: Final[Player]
    player_list: Final[arcade.SpriteList[Player]]
    grounds: Final[arcade.SpriteList]
    walls: Final[arcade.SpriteList]
    crystals: Final[arcade.SpriteList]
    keys_down: set[int]
    spinners: Final[arcade.SpriteList]
    spinners_info: list[SpinnerInfo]
    holes: Final[arcade.SpriteList]
    bats: Final[arcade.SpriteList]
    bats_info: list[BatInfo]
    rng: random.Random
    ui_camera: Final[arcade.camera.Camera2D]
    score: int
    score_text: arcade.Text


    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]


    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()
        self.map = map
        self.player = Player()
        self.player.center_x = grid_to_pixels(map.player_start_x)
        self.player.center_y = grid_to_pixels(map.player_start_y)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList(use_spatial_hash=True)
        self.spinners = arcade.SpriteList()
        self.spinners_info = []
        self.holes = arcade.SpriteList(use_spatial_hash=True)
        self.bats = arcade.SpriteList()
        self.bats_info = []
        self.rng = random.Random()
        self.ui_camera = arcade.camera.Camera2D()
        self.score = 0
        self.score_text = arcade.Text(text=f"Score: {self.score}",
            x=20,
            y=self.window.height - 40 if self.window else 20,
            color=arcade.color.WHITE,
            font_size=20,
        )

        self.weapon_icon = arcade.Sprite(scale=2) #creer un sprite pour afficher l'arme
        self.weapon_icon.center_x = 50
        self.weapon_icon.center_y = 50

        self.weapon = Weapon(self.player.center_x, self.player.center_y)


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

                    min_x, max_x = spinner_horizontal_limits(self.map, x, y)

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

                    min_y, max_y = spinner_vertical_limits(self.map, x, y)

                    self.spinners_info.append(
                        SpinnerInfo(
                            sprite=spinner,
                            horizontal=False,
                            min_pos=grid_to_pixels(min_y),
                            max_pos=grid_to_pixels(max_y),
                            speed=3,
                        )
                    )
                elif cell == GridCell.HOLE:
                    hole = arcade.Sprite(
                        TEXTURE_HOLE, scale=SCALE,
                        center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                    )
                    self.holes.append(hole)
                elif cell == GridCell.BAT:
                    bat = arcade.Sprite( scale=SCALE,)
                    bat.textures = BAT_TEXTURES
                    bat.texture = BAT_TEXTURES[0]
                    bat.cur_texture_index = 0 # permet de savoir quelle frame de l'animation on affiche
                    bat.center_x = grid_to_pixels(x)
                    bat.center_y = grid_to_pixels(y)
                    self.bats.append(bat)
                    min_x = max(0, x-4)
                    max_x = min(self.map.width-1, x+4)
                    min_y = max(0, y-3)
                    max_y = min(self.map.height-1, y+3)
                    self.bats_info.append(
                        BatInfo(
                            sprite=bat,
                            min_x=grid_to_pixels(min_x),
                            max_x=grid_to_pixels(max_x),
                            min_y=grid_to_pixels(min_y),
                            max_y=grid_to_pixels(max_y),
                            vx=2.0,
                            vy=0.0,
                        )
                    )


        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

    def _player_falls_into_hole(self) -> bool:
        for hole in arcade.get_sprites_at_point(self.player.position, self.holes): #permet de tester seulement les trous qui sont proches du joueur
            dx = self.player.center_x - hole.center_x
            dy = self.player.center_y - hole.center_y
            if dx * dx + dy * dy <= 16 * 16:
                return True
        return False

    def boomerang_hits_bush(self) -> bool:
        grid_x = int(self.weapon.sprite.center_x // TILE_SIZE)
        grid_y = int(self.weapon.sprite.center_y // TILE_SIZE)

        if grid_x < 0 or grid_x >= self.map.width or grid_y < 0 or grid_y >= self.map.height:
            return True

        return self.map.get_cell(grid_x, grid_y) == GridCell.BUSH

    def check_boomerang_hits_monsters(self) -> bool:
        hit_something = False

        for spinner in list(self.spinners):
            dx = self.weapon.sprite.center_x - spinner.center_x
            dy = self.weapon.sprite.center_y - spinner.center_y

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= TILE_SIZE / 2: # /2 car il faut s'assurer qu'il soit sur la même case
                spinner.remove_from_sprite_lists() # supprime le spinner visuellement
                for info in self.spinners_info: # enleve le spinner dans la logique du jeu
                    if info.sprite == spinner:
                        self.spinners_info.remove(info)
                        break

                hit_something = True
        for bat in list(self.bats):
            dx = self.weapon.sprite.center_x - bat.center_x
            dy = self.weapon.sprite.center_y - bat.center_y

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= TILE_SIZE / 2:
                bat.remove_from_sprite_lists()
                for info in self.bats_info:
                    if info.sprite == bat:
                        self.bats_info.remove(info)
                        break

                hit_something = True

        return hit_something

    def check_epee_hits(self) -> None:
        for spinner in list(self.spinners):
            if arcade.check_for_collision(self.weapon.sprite, spinner): # fonction de Arcade qui mermet de tester les collisions
                spinner.remove_from_sprite_lists()
                for info in self.spinners_info: # retire visuellement et techniquement
                    if info.sprite == spinner:
                        self.spinners_info.remove(info)
                        break
        for crystal in list(self.crystals):
            if arcade.check_for_collision(self.weapon.sprite, crystal):
                arcade.play_sound(SOUND_COIN)
                crystal.remove_from_sprite_lists()
                self.score += 1
                self.score_text.text = f"Score: {self.score}"
        for bat in list(self.bats):
            if arcade.check_for_collision(self.weapon.sprite, bat):
                bat.remove_from_sprite_lists()
                for info in self.bats_info:
                    if info.sprite == bat:
                        self.bats_info.remove(info)
                        break


    def update_weapon_icon(self) -> None: # determine quel arme affiché
        if self.weapon.weapon_type == WeaponType.BOOMERANG:
            self.weapon_icon.texture = WEAPON_ICON_BOOMERANG
        else:
            self.weapon_icon.texture = WEAPON_ICON_EPEE

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
         self.clear()
         with self.camera.activate():
                self.grounds.draw()
                self.holes.draw()
                self.walls.draw()
                self.crystals.draw()
                self.spinners.draw()
                self.bats.draw()
                if self.weapon.is_active():
                    arcade.draw_sprite(self.weapon.sprite)
                if not (self.weapon.weapon_type == WeaponType.EPEE and self.weapon.state == WeaponState.ACTIVE): # permet l'affichage du joeur ssi l'épée est inacivité
                    self.player_list.draw()
         with self.ui_camera.activate():
            self.score_text.y = self.window.height - 40
            self.score_text.draw()
            self.update_weapon_icon()
            self.weapon_icon.center_x = 60
            self.weapon_icon.center_y = self.window.height - 60
            arcade.draw_sprite(self.weapon_icon)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(GameView(self.map))
            return

        if self.weapon.weapon_type == WeaponType.EPEE and self.weapon.state == WeaponState.ACTIVE:
            return

        if symbol == arcade.key.R:
            self.weapon.change_weapon_type()
            return

        if symbol == arcade.key.D:
            self.weapon.use(self.player.center_x, self.player.center_y, self.player.direction)
            return # empeche la touche D d'etre traiter pour autre chose

        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if self.weapon.weapon_type == WeaponType.EPEE and self.weapon.state == WeaponState.ACTIVE:
            return
        self.player.on_key_release(symbol, modifiers)

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()
        self.crystals.update_animation()
        self.player.update_animation_state(delta_time)
        update_camera(self.camera, self.player, self.window, self.world_width, self.world_height)
        hit_list = arcade.check_for_collision_with_list(self.player, self.crystals)
        for crystal in hit_list:
            arcade.play_sound(SOUND_COIN)
            crystal.remove_from_sprite_lists()
            self.score += 1
            self.score_text.text = f"Score: {self.score}"
        update_spinners(self.spinners_info)
        self.spinners.update()
        if self._player_falls_into_hole():
            self.window.show_view(GameView(self.map))
            return

        self.spinners.update_animation()

        update_bats(self.bats_info, self.rng)
        for bat in self.bats:
             bat.cur_texture_index = (bat.cur_texture_index + 1) % len(bat.textures) # change la frame de l'animation pour faire bouger les ailes des chauves-souris
             bat.texture = bat.textures[bat.cur_texture_index]

        if self.weapon.weapon_type == WeaponType.BOOMERANG:
            if self.weapon.state == WeaponState.LAUNCHING:
                self.weapon.update_launching()

                if self.check_boomerang_hits_monsters():
                    self.weapon.switch_to_returning()
                elif self.boomerang_hits_bush():
                    self.weapon.switch_to_returning()
                elif self.weapon.reached_max_distance():
                    self.weapon.switch_to_returning()

            elif self.weapon.state == WeaponState.RETURNING:
                self.weapon.update_returning(self.player.center_x, self.player.center_y)

                self.check_boomerang_hits_monsters()

                if self.weapon.is_close_to_player(self.player.center_x, self.player.center_y):
                    self.weapon.deactivate(self.player.center_x, self.player.center_y)
        elif self.weapon.weapon_type == WeaponType.EPEE:
            if self.weapon.state == WeaponState.ACTIVE:
                self.weapon.update_epee(delta_time)
                self.check_epee_hits()

        collisions = arcade.check_for_collision_with_list(self.player, self.spinners)

        if len(collisions) > 0:
            self.window.show_view(GameView(self.map))
            return

        if arcade.check_for_collision_with_list(self.player, self.bats):
            self.window.show_view(GameView(self.map))
            return
