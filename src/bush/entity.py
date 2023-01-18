"""
entity
 - basic entity class
 - entity container group
"""
from copy import deepcopy

import pygame


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, pos, surface=None, groups=(), id=None):
        super().__init__(*groups)
        self.image = surface
        if surface is None:
            self.image = pygame.Surface((0, 0))
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)
        self._layer = 1
        self._id = id

    def get_id(self):
        return deepcopy(self._id)

    def limit(self, map_rect):
        pass  # Static Entities don't move

    def update(self, dt):
        self.rect.center = self.pos


class Actor(Entity):
    def __init__(self, pos, surface=None, groups=(), id=None):
        super().__init__(pos, surface, groups, id)
        self.velocity = pygame.Vector2()

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

    def limit(self, map_rect):
        moved = False
        difference = max(map_rect.top - self.rect.top, 0)
        self.pos.y += difference
        moved |= difference
        difference = min(map_rect.bottom - self.rect.bottom, 0)
        self.pos.y += difference
        moved |= difference
        difference = max(map_rect.left - self.rect.left, 0)
        self.pos.x += difference
        moved |= difference
        difference = min(map_rect.right - self.rect.right, 0)
        self.pos.x += difference
        moved |= difference
        self.rect.center = self.pos
        return moved
