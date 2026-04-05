import arcade
import math

from enum import Enum

from constants import TILE_SIZE, SCALE
from textures import (
    BOOMERANG_TEXTURES,
    EPEE_UP_TEXTURES,
    EPEE_DOWN_TEXTURES,
    EPEE_LEFT_TEXTURES,
    EPEE_RIGHT_TEXTURES,
)

from player import Direction

class WeaponType(Enum): # changer le enum car ce n'est pas un enum ici
    BOOMERANG = 0
    EPEE = 1

class WeaponState(Enum): # meme chose que pour le type d'arme, ce n'est pas un enum
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
