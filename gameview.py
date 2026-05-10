from typing import Final
import math
import arcade
import random
import cProfile

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
    SLIME_TEXTURES,
    TEXTURE_SWITCH_OFF,
    TEXTURE_GATE_CLOSED,
)
from map import Map, GridCell
from player import Player
from weapon import Weapon, WeaponType, WeaponState
from spinner import SpinnerInfo, spinner_horizontal_limits, spinner_vertical_limits, update_spinners
from camera import update_camera
from bats import BatInfo, update_bats
from slimes import SlimeInfo, slime_possible_destinations, choose_new_destination, update_slimes
from gate import GateInfo, SwitchInfo, update_all_gates, update_switch_texture

LEFT_MARGIN = 200
RIGHT_MARGIN = 200
BOTTOM_MARGIN = 200
TOP_MARGIN = 200

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

def remove_info_for_sprite(infos: list, sprite: arcade.Sprite) -> None:
    for info in infos:
        if info.sprite == sprite:
            infos.remove(info)
            return

def animate_sprite(sprites: arcade.SpriteList) -> None: # fait avancer l'animation d'une liste de sprite en changeant leur texture
    for sprite in sprites:
        sprite.cur_texture_index = (sprite.cur_texture_index + 1) % len(sprite.textures)
        sprite.texture = sprite.textures[sprite.cur_texture_index]

class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]
    profiler: cProfile.Profile
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
    slimes: Final[arcade.SpriteList]
    slimes_info: list[SlimeInfo]
    rng: random.Random
    ui_camera: Final[arcade.camera.Camera2D]
    score: int
    score_text: arcade.Text
    switches: Final[arcade.SpriteList]
    gates: Final[arcade.SpriteList]
    switches_info: list[SwitchInfo]
    gates_info: list[GateInfo]

    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]


    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()
        self.profiler = cProfile.Profile()
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
        self.slimes = arcade.SpriteList()
        self.slimes_info = []
        self.rng = random.Random()
        self.ui_camera = arcade.camera.Camera2D()
        self.score = 0
        self.score_text = arcade.Text(text=f"Score: {self.score}",
            x=20,
            y=self.window.height - 40 if self.window else 20,
            color=arcade.color.WHITE,
            font_size=20,
        )
        self.switches = arcade.SpriteList()
        self.gates = arcade.SpriteList()
        self.switches_info = []
        self.gates_info = []

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
                elif cell == GridCell.SLIME:
                    slime = arcade.Sprite(scale=SCALE)
                    slime.textures = SLIME_TEXTURES
                    slime.texture = SLIME_TEXTURES[0]
                    slime.cur_texture_index = 0
                    slime.center_x = grid_to_pixels(x)
                    slime.center_y = grid_to_pixels(y)
                    self.slimes.append(slime)
                    possible_destinations = slime_possible_destinations(self.map, x, y, TILE_SIZE)
                    slime_info = SlimeInfo(
                        sprite=slime,
                        start_x=x,
                        start_y=y,
                        possible_destinations=possible_destinations,
                        current_path=[],
                        path_index=0,
                        speed=1.0,
                        target_node=None,
                    )
                    choose_new_destination(slime_info, self.rng, self.map)
                    self.slimes_info.append(slime_info)

        for switch_config in self.map.switches:
            switch = arcade.Sprite(TEXTURE_SWITCH_OFF, scale=0.25)
            switch.center_x = grid_to_pixels(switch_config.x)
            switch.center_y = grid_to_pixels(switch_config.y)
            self.switches.append(switch)

            switch_info = SwitchInfo(
                id=switch_config.id,
                sprite=switch,
                is_on=switch_config.is_on,
            )
            update_switch_texture(switch_info)
            self.switches_info.append(switch_info)

        for gate_config in self.map.gates:
            gate = arcade.Sprite(TEXTURE_GATE_CLOSED, scale=SCALE)
            gate.center_x = grid_to_pixels(gate_config.x)
            gate.center_y = grid_to_pixels(gate_config.y)
            self.gates.append(gate)

            self.gates_info.append(
                GateInfo(
                    sprite=gate,
                    condition=gate_config.open_if,
                    is_open=False,
                )
            )
        update_all_gates(self.gates_info, self.switches_info, self.walls)

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

        return len(arcade.check_for_collision_with_list(self.weapon.sprite, self.walls)) > 0

    def weapon_hits_sprite(self, sprite: arcade.Sprite) -> bool:
        dx = self.weapon.sprite.center_x - sprite.center_x
        dy = self.weapon.sprite.center_y - sprite.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= TILE_SIZE / 2

    def check_boomerang_hits_monsters(self) -> bool:
        hit_something = False

        for spinner in list(self.spinners):
            if self.weapon_hits_sprite(spinner):
                spinner.remove_from_sprite_lists()
                remove_info_for_sprite(self.spinners_info, spinner)
                hit_something = True
        for bat in list(self.bats):
            if self.weapon_hits_sprite(bat):
                bat.remove_from_sprite_lists()
                remove_info_for_sprite(self.bats_info, bat)
                hit_something = True
        for slime in list(self.slimes):
            if self.weapon_hits_sprite(slime):
                slime.remove_from_sprite_lists()
                remove_info_for_sprite(self.slimes_info, slime)
                hit_something = True
        for slime in list(self.slimes):
            if self.weapon_hits_sprite(slime):
                slime.remove_from_sprite_lists()
                remove_info_for_sprite(self.slimes_info, slime)
                hit_something = True

        return hit_something

    def check_epee_hits(self) -> None:
        for spinner in list(self.spinners):
            if arcade.check_for_collision(self.weapon.sprite, spinner): # fonction de Arcade qui mermet de tester les collisions
                spinner.remove_from_sprite_lists()
                remove_info_for_sprite(self.spinners_info, spinner)
        for crystal in list(self.crystals):
            if arcade.check_for_collision(self.weapon.sprite, crystal):
                arcade.play_sound(SOUND_COIN)
                crystal.remove_from_sprite_lists()
                self.score += 1
                self.score_text.text = f"Score: {self.score}"
        for bat in list(self.bats):
            if arcade.check_for_collision(self.weapon.sprite, bat):
                bat.remove_from_sprite_lists()
                remove_info_for_sprite(self.bats_info, bat)
        for slime in list(self.slimes):
            if arcade.check_for_collision(self.weapon.sprite, slime):
                slime.remove_from_sprite_lists()
                remove_info_for_sprite(self.slimes_info, slime)

    def check_weapon_hits_switches(self) -> bool:
        if self.weapon.has_hit_switch:
            return False

        for switch_info in self.switches_info:
            if arcade.check_for_collision(self.weapon.sprite, switch_info.sprite):
                self.weapon.has_hit_switch = True
                switch_info.is_on = not switch_info.is_on
                update_switch_texture(switch_info)
                update_all_gates(self.gates_info, self.switches_info, self.walls)
                return True

        return False

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
                self.slimes.draw()
                self.gates.draw()
                self.switches.draw()
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
        self.profiler.enable()
        self.physics_engine.update()
        self.profiler.disable()
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
        animate_sprite(self.bats)

        update_slimes(self.slimes_info, self.rng, self.map, TILE_SIZE, self.player, self.walls)
        animate_sprite(self.slimes)

        if self.weapon.weapon_type == WeaponType.BOOMERANG:
            if self.weapon.state == WeaponState.LAUNCHING:
                self.weapon.update_launching()

                if self.check_weapon_hits_switches():
                    self.weapon.switch_to_returning()
                elif self.check_boomerang_hits_monsters():
                    self.weapon.switch_to_returning()
                elif self.boomerang_hits_bush():
                    self.weapon.switch_to_returning()
                elif self.weapon.reached_max_distance():
                    self.weapon.switch_to_returning()

            elif self.weapon.state == WeaponState.RETURNING:
                self.weapon.update_returning(self.player.center_x, self.player.center_y)

                self.check_weapon_hits_switches()
                self.check_boomerang_hits_monsters()

                if self.weapon.is_close_to_player(self.player.center_x, self.player.center_y):
                    self.weapon.deactivate(self.player.center_x, self.player.center_y)
        elif self.weapon.weapon_type == WeaponType.EPEE:
            if self.weapon.state == WeaponState.ACTIVE:
                self.weapon.update_epee(delta_time)
                self.check_weapon_hits_switches()
                self.check_epee_hits()

        for monsters in (self.spinners, self.bats, self.slimes):
            if arcade.check_for_collision_with_list(self.player, monsters):
                self.window.show_view(GameView(self.map))
                return
