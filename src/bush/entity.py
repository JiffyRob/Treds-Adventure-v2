"""
entity
 - basic entity class
 - entity container group
"""
from copy import deepcopy
import pygame


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, surface, pos, groups=(), id=None):
        super().__init__(*groups)
        self.image = surface
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()
        self.rect = self.image.get_rect(center=self.pos)
        self._layer = 1
        self._id = id

    def get_id(self):
        return deepcopy(self._id)

    def control(self, dt):
        pass

    def physics_update(self, dt):
        pass

    def behaviour_update(self, dt):
        pass

    def render(self, dt):
        pass

    def update(self, dt):
        self.rect.center = self.pos
        self.control(dt)
        self.physics_update(dt)
        self.behaviour_update(dt)
        self.render(dt)

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


class EntityLite(pygame.sprite.Sprite):
    def __init__(self, surface, pos):
        self.pos = pos
        self.image = surface
        self.rect = self.image.get_rect(center=self.pos)
        self._layer = 1
        super().__init__()

    def update(self):
        self.rect.center = self.pos

    def limit(self, *args, **kwargs):
        pass
