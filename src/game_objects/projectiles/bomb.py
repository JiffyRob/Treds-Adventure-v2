import pygame

import globals
import particle_util
from game_objects.projectiles import base


class Bomb(base.Projectile):
    def __init__(self, data):
        data.surface = pygame.Surface((16, 16))  # TODO: make bomb art
        super().__init__(data, 3500)

    def on_death(self):
        particle_util.explosion(
            self.pos, globals.engine.stack.get_current().particle_manager
        )


class BigBomb(base.Projectile):
    ...


class BiggerBomb(base.Projectile):
    ...


class BiggestBomb(base.Projectile):
    ...


class BiggesterBomb(base.Projectile):
    ...
