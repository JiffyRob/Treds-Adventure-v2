"""
level
 - basic mapping primitives
"""
import os

import pygame
import pytmx
import pytmx.util_pygame as pytmx

from bush import physics


class PhysicsGroup(pygame.sprite.Group):
    """Group of entities that have physics bodies"""

    def __init__(self, *sprites):
        self.body_group = physics.BodyGroup()
        super().__init__(*sprites)

    def get_bodies(self, sprites=None):
        sprites = sprites or self.body_group.sprites()
        for sprite in sprites:
            yield sprite.body

    def add(self, *sprites):
        super().add(*sprites)
        self.body_group.add(*self.get_bodies(sprites))

    def remove(self, *sprites):
        super().remove(*sprites)
        self.body_group.remove(*self.get_bodies(sprites))

    def update(self, dt):
        self.body_group.update(dt)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, cam_size, map_size, pos, follow=None, *sprites):
        super().__init__(*sprites)
        self.cam_rect = pygame.Rect(0, 0, *cam_size)
        self.map_rect = pygame.Rect(0, 0, *map_size)
        self.cam_rect.center = pos
        self.follow = follow

    def draw(self, surface):
        if self.follow is not None:
            self.cam_rect.center = self.follow.pos
            self.limit()
            self.limit_sprites()
        offset = pygame.Vector2(self.cam_rect.topleft)
        for sprite in self.sprites():
            pos = pygame.Vector2(sprite.rect.topleft) - offset
            surface.blit(sprite.image, pos)

    def limit(self):
        if self.cam_rect.height < self.map_rect.height:
            self.cam_rect.top = max(self.cam_rect.top, self.map_rect.top)
            self.cam_rect.bottom = min(self.cam_rect.bottom, self.map_rect.bottom)
        else:
            self.cam_rect.centery = self.map_rect.centery

        if self.cam_rect.width < self.map_rect.width:
            self.cam_rect.left = max(self.cam_rect.left, self.map_rect.left)
            self.cam_rect.right = min(self.cam_rect.right, self.map_rect.right)
        else:
            self.cam_rect.centerx = self.map_rect.centerx

    def limit_sprites(self):
        for sprite in self.sprites():
            difference = max(self.map_rect.top - sprite.rect.top, 0)
            sprite.pos.y += difference
            difference = min(self.map_rect.bottom - sprite.rect.bottom, 0)
            sprite.pos.y += difference
            difference = max(self.map_rect.left - sprite.rect.left, 0)
            sprite.pos.x += difference
            difference = min(self.map_rect.right - sprite.rect.right, 0)
            sprite.pos.x += difference
            sprite.rect.center = sprite.pos


class TopDownGroup(CameraGroup):
    def sprites(self):
        def sortkey(sprite):
            return sprite.rect.bottom

        return sorted(super().sprites(), key=sortkey)
