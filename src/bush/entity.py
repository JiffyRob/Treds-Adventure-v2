"""
entity
 - basic entity class
 - entity container group
"""
from copy import deepcopy

import pygame


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, pos, surface=None, groups=(), id=None, layer=None):
        super().__init__(*groups)
        self.image = surface
        if surface is None:
            self.image = pygame.Surface((0, 0))
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)
        self._layer = 1
        if layer is not None:
            self._layer = layer
        self._id = id

    def get_id(self):
        return deepcopy(self._id)

    def limit(self, map_rect):
        pass  # Static Entities don't move

    def update(self, dt):
        self.rect.center = self.pos


class Actor(Entity):
    def __init__(self, pos, surface=None, groups=(), id=None, layer=None):
        super().__init__(pos, surface, groups, id, layer)
        self.velocity = pygame.Vector2()

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

    def pos_after_limiting(self, map_rect):
        pos = self.pos.copy()
        difference = max(map_rect.top - self.rect.top, 0)
        pos.y += difference
        difference = min(map_rect.bottom - self.rect.bottom, 0)
        pos.y += difference
        difference = max(map_rect.left - self.rect.left, 0)
        pos.x += difference
        difference = min(map_rect.right - self.rect.right, 0)
        pos.x += difference
        return pos

    def limit(self, map_rect):
        old_pos = self.pos.copy()
        new_pos = self.pos_after_limiting(map_rect)
        self.rect.center = self.pos = new_pos
        return new_pos == old_pos
