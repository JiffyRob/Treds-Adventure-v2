import pygame

import globals
import particle_util
from bush import animation, asset_handler, timer
from game_objects.projectiles import base

loader = asset_handler.AssetHandler("sprites/projectiles")


class Bomb(base.Projectile):
    def __init__(self, data):
        self.frames = loader.load_spritesheet("bomb.png", (16, 16))
        print(len(self.frames))
        self.flipped = False
        data.surface = animation.Animation(self.frames[:6], 100)
        super().__init__(data, 5000)

    def update(self, dt):
        super().update(dt)
        if self.life_timer.time_left() < 1000 and not self.flipped:
            self.anim = animation.Animation(self.frames[6:], 150)
            self.flipped = True

    def on_death(self):
        particle_util.explosion(
            self.pos, globals.engine.stack.get_current().particle_manager, 6, 0, 0, 1, 0
        )
        max_dist = 32
        max_damage = 10
        for sprite in self.registry.get_group("attackable").sprites():
            dist = (sprite.pos - self.pos).length()
            if dist < max_dist:
                # damage is proportional to distance from the bomb
                damage = (1 - (dist / max_dist)) * max_damage
                sprite.hurt(round(damage))


class BigBomb(base.Projectile):
    ...


class BiggerBomb(base.Projectile):
    ...


class BiggestBomb(base.Projectile):
    ...


class BiggesterBomb(base.Projectile):
    ...
