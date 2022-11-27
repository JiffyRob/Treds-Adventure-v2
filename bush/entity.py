"""
entity
 - basic entity class
 - entity container group
"""
from typing import Iterable, Sequence, Union

import pygame

from bush import util


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, surface, pos, groups):
        super().__init__(*groups)
        self.image = surface
        self.pos = pygame.Vector2(pos)
        self.state = None
        self.velocity = pygame.Vector2()

    def input(self, dt):
        pass

    def physics_update(self, dt):
        pass

    def behaviour_update(self, dt):
        pass

    def render(self, dt):
        pass

    def update(self, dt):
        self.input(dt)
        self.physics_update(dt)
        self.state_update(dt)
        self.render(dt)
