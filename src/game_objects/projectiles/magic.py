import pygame.sprite

import globals
from bush import animation, asset_handler, collision
from game_objects.projectiles import base


class Lightening(base.Projectile):
    def __init__(self, data):
        data.surface = animation.OnceAnimation(
            asset_handler.glob_loader.load_spritesheet(
                "particles/lightening.png", (20, 28)
            ),
            50,
        )
        super().__init__(data, 500)
        self.collision_rect = pygame.Rect(0, 0, 16, 16)
        self.collision_rect.midbottom = self.rect.midbottom
        self.attacked = []

    def update(self, dt):
        super().update(dt)
        collided = pygame.sprite.spritecollideany(
            self,
            self.registry.get_group("attackable"),
            collision.collision_rect_collide,
        )
        if collided not in self.attacked + [None, globals.player]:
            collided.hurt(3)
            self.attacked.append(collided)
