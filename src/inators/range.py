import pygame

import globals
from game_objects import arg
from game_objects.projectiles import bomb
from inators import base


class Boominator(base.Inator):
    """Goes boom"""

    def can_be_used(self):
        return super().can_be_used() and globals.player.has("bomb")

    def use_callback(self):
        bomb.Bomb(arg.from_projectile_shooter(globals.player, pygame.Vector2()))
        globals.player.lose("bomb")
