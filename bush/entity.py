"""
entity
 - basic entity class
 - entity container group
"""
import queue
from typing import Iterable, Sequence, Union

import pygame

from bush import util


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    def __init__(self, surface, pos, groups=()):
        super().__init__(*groups)
        self.image = surface
        self.pos = pygame.Vector2(pos)
        self.state = None
        self.velocity = pygame.Vector2()
        self.rect = self.image.get_rect(center=self.pos)
        self.events = queue.SimpleQueue()
        self.command_dict = {"move": self.move, "die": self.kill, "idle": self.stop}
        self.script_acceptable_names = {
            "pos",
            "velocity",
            "state",
            "rect",
            "events",
            "command",
        }

    def to_scripting_dict(self):
        scripting_dict = {}
        for key in self.__dict__:
            if key in self.script_acceptable_names:
                scripting_dict[key] = self.__dict__[key]
        return scripting_dict

    def move(self, veloc):
        self.velocity += veloc

    def stop(self):
        self.velocity = pygame.Vector2()

    def input(self, dt):
        pass

    def event(self, event):
        self.events.put(event)

    def physics_update(self, dt):
        pass

    def behaviour_update(self, dt):
        pass

    def command(self, command, *args, **kwargs):
        callback = self.command_dict.get(command, lambda *x, **y: None)
        callback(*args, **kwargs)

    def render(self, dt):
        pass

    def update(self, dt):
        self.rect.center = self.pos
        self.input(dt)
        self.physics_update(dt)
        self.behaviour_update(dt)
        self.render(dt)
