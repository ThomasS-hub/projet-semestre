from typing import Final
import arcade
from textures import *
from textures import SOUND_COIN
from map import Map, GridCell
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from constants import *
import math

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

class WeaponType(Enum):
    BOOMERANG = 0
    EPEE = 1

class WeaponState(Enum):
    INACTIVE = 0
    LAUNCHING = 1      # pour le boomerang
    RETURNING = 2      # pour le boomerang
    ACTIVE = 3         # pour l'épée

class Weapon:
    def __init__(self, start_x: float, start_y: float) -> None:
        self.weapon_type = WeaponType.BOOMERANG
        self.state = WeaponState.INACTIVE # initialise la position du boomerang

        self.sprite = arcade.Sprite(scale=1)#scale=SCALE afiche le sprite en le multipliant par 1
        self.sprite.center_x = start_x
        self.sprite.center_y = start_y

        self.dx = 0.0
        self.dy =0.0

        self.distance_travelled = 0.0
        self.max_distance = 8 * TILE_SIZE
        self.speed = 8

        self.time = 0.0
        self.attack_duration = 6 * 0.05

        self.sprite.cur_texture_index = 0 # on actualise a la premiere image de la banque
        self.set_scale()
        self.set_boomerang_textures()


    def set_weapon_type(self, weapon_type: WeaponType) -> None:
        self.weapon_type = weapon_type
        self.state = WeaponState.INACTIVE
        self.sprite.cur_texture_index = 0
        self.set_scale()

        if weapon_type == WeaponType.BOOMERANG:
            self.set_boomerang_textures()
        else:
            self.set_epee_textures(Direction.South)

    def set_scale(self) -> None:
        if self.weapon_type == WeaponType.BOOMERANG:
            self.sprite.scale = SCALE
        else:  # EPEE
            self.sprite.scale = 1.3

    def is_active(self) -> bool:
        return self.state != WeaponState.INACTIVE

    def change_weapon_type(self) -> None:
        if self.is_active(): # ne fait rien si une arme est déjà active
            return
        # passer d'une arme a l'autre
        if self.weapon_type == WeaponType.BOOMERANG:
            self.set_weapon_type(WeaponType.EPEE)
        else:
            self.set_weapon_type(WeaponType.BOOMERANG)

    def set_boomerang_textures(self) -> None:
        self.sprite.textures = BOOMERANG_TEXTURES # donne au sprite toutes les images du boomerang
        self.sprite.texture = BOOMERANG_TEXTURES[0] # initialise a la première image
        self.sprite.cur_texture_index = 0 # commence l'anim a la frame 0

    def set_epee_textures(self, direction: Direction) -> None: # calibre l'image de l'epee en fonction de la position du joueur
        if direction == Direction.North: # adapte l'animation a la direction du joueur
            textures = EPEE_UP_TEXTURES
        elif direction == Direction.South:
            textures = EPEE_DOWN_TEXTURES
        elif direction == Direction.West:
            textures = EPEE_LEFT_TEXTURES
        else:
            textures = EPEE_RIGHT_TEXTURES

        self.sprite.textures = textures
        self.sprite.texture = textures[0]
        self.sprite.cur_texture_index = 0

    def use(self, player_x: float, player_y: float, direction: Direction) -> None: # initialise chaque lancé
        if self.is_active(): # empêche d'utliser deux fois une arme en même temps
            return

        if self.weapon_type == WeaponType.BOOMERANG:
            self.use_boomerang(player_x, player_y, direction) # appelle méthode boomerang
        else:
            self.use_epee(player_x, player_y, direction) # appelle méthode epee

    def use_epee(self, player_x: float, player_y: float, direction: Direction) -> None:
        self.state = WeaponState.ACTIVE
        self.time = 0.0

        offset = int(1.25 * TILE_SIZE) # décalage de l'épée vers l'avant du joeur
        if direction == Direction.North:
            self.sprite.center_x = player_x
            self.sprite.center_y = player_y + offset
        elif direction == Direction.South:
            self.sprite.center_x = player_x
            self.sprite.center_y = player_y - offset
        elif direction == Direction.West:
            self.sprite.center_x = player_x - offset
            self.sprite.center_y = player_y
        else:
            self.sprite.center_x = player_x + offset
            self.sprite.center_y = player_y

        self.set_epee_textures(direction)

    def update_epee(self, delta_time: float) -> None:
        self.time += delta_time
        index = int(self.time / 0.05) # temps écoulé / durée d'une frame = numéro de la frame (image a afficher)

        if index >= len(self.sprite.textures): # si le index est superieur est nombre d'image alors l'image est terminé
            self.state = WeaponState.INACTIVE
            return
        self.sprite.cur_texture_index = index
        self.sprite.texture = self.sprite.textures[index]


    def use_boomerang(self, player_x: float, player_y: float, direction: Direction) -> None:
        self.state = WeaponState.LAUNCHING
        self.distance_travelled = 0.0

        self.sprite.center_x = player_x
        self.sprite.center_y = player_y

        self.dx, self.dy = direction.to_vector() # permet de cree le vectuer de deplacement reutiliser dans update_launching pour savoir dans quelle direction aller
        self.set_boomerang_textures()

    def update_launching(self) -> None:
        self.sprite.center_x += self.dx * self.speed
        self.sprite.center_y += self.dy * self.speed
        self.distance_travelled += self.speed # car la vitesse pendant un frame est la distance parcouru pendant ce frame
        self.sprite.cur_texture_index = (self.sprite.cur_texture_index + 1) % len(self.sprite.textures) # permet de tourne en boucle sur les différentes animation
        self.sprite.texture = self.sprite.textures[self.sprite.cur_texture_index]

    def update_returning(self, player_x: float, player_y: float) -> None:
        dx = player_x - self.sprite.center_x
        dy = player_y - self.sprite.center_y
        distance = math.sqrt(dx * dx + dy * dy) # norme de la distance entre le joueur et le boomerang

        if distance == 0:
            self.state = WeaponState.INACTIVE
            return

        direction_x = dx / distance # nous donne la direction seulement en diviasant par la norme
        direction_y = dy / distance

        self.sprite.center_x += direction_x * self.speed # on multip:ie la direction par la vitesse
        self.sprite.center_y += direction_y * self.speed
        self.sprite.cur_texture_index = (self.sprite.cur_texture_index + 1) % len(self.sprite.textures)
        self.sprite.texture = self.sprite.textures[self.sprite.cur_texture_index]

    def is_close_to_player(self, player_x: float, player_y: float) -> bool:
        dx = player_x - self.sprite.center_x
        dy = player_y - self.sprite.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.speed

    def reached_max_distance(self) -> bool:
        return self.distance_travelled >= self.max_distance

    def deactivate(self, player_x: float, player_y: float) -> None:
        self.state = WeaponState.INACTIVE
        self.sprite.center_x = player_x
        self.sprite.center_y = player_y

    def switch_to_returning(self) -> None:
        self.state = WeaponState.RETURNING


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
                elif cell == GridCell.HOLE:
                    hole = arcade.Sprite(
                        TEXTURE_HOLE, scale=SCALE,
                        center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                    )
                    self.holes.append(hole)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

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

    def check_boomerang_hits_spinners(self) -> bool:
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
        self.physics_engine.update()
        self.crystals.update_animation()
        self.player.update_animation_state(delta_time)
        self._update_camera()
        hit_list = arcade.check_for_collision_with_list(self.player, self.crystals)
        for crystal in hit_list:
            arcade.play_sound(SOUND_COIN)
            crystal.remove_from_sprite_lists()
            self.score += 1
            self.score_text.text = f"Score: {self.score}"
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
        if self._player_falls_into_hole():
            self.window.show_view(GameView(self.map))
            return

        self.spinners.update_animation()

        if self.weapon.weapon_type == WeaponType.BOOMERANG:
            if self.weapon.state == WeaponState.LAUNCHING:
                self.weapon.update_launching()

                if self.check_boomerang_hits_spinners():
                    self.weapon.switch_to_returning()
                elif self.boomerang_hits_bush():
                    self.weapon.switch_to_returning()
                elif self.weapon.reached_max_distance():
                    self.weapon.switch_to_returning()

            elif self.weapon.state == WeaponState.RETURNING:
                self.weapon.update_returning(self.player.center_x, self.player.center_y)

                self.check_boomerang_hits_spinners()

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
