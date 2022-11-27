"""
entity
 - basic entity class
 - entity container group
"""
from typing import Iterable, Sequence, Union

import pygame
import queue

from bush import util


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, surface, pos, groups):
        super().__init__(*groups)
        self.image = surface
        self.pos = pygame.Vector2(pos)
        self.state = None
        self.velocity = pygame.Vector2()
        self.rect = self.image.get_rect(center=self.pos)
        self.events = queue.SimpleQueue()

    def input(self, dt):
        pass

    def event(self, event):
        self.events.put(event)

    def physics_update(self, dt):
        print(self.velocity, dt)
        self.pos += self.velocity * dt
        self.rect.center = self.pos

    def behaviour_update(self, dt):
        pass

    def render(self, dt):
        pass

    def update(self, dt):
        self.input(dt)
        self.physics_update(dt)
        self.behaviour_update(dt)
        self.render(dt)
