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
        self.velocity = pygame.Vector2()
        self.rect = self.image.get_rect(center=self.pos)
        self.commands = queue.SimpleQueue()
        self.controller = None
        self.current_command = None
        self.script_acceptable_names = {
            "pos",
            "velocity",
            "state",
            "rect",
            "events",
            "command",
        }
        self._layer = 1

    def move(self, veloc):
        self.velocity += veloc

    def stop(self):
        self.velocity = pygame.Vector2()

    def control(self, dt):
        if self.controller:
            commands = self.controller.generate_command(self)
            for command in commands:
                command(self)

    def event(self, event):
        if self.controller:
            if self.controller.accepts_events:
                self.controller.event(event)

    def command_update(self, dt):
        if self.current_command is None:
            while not self.commands.empty():
                command = self.commands.get()
                command()
                if not command.done():
                    self.current_command = command
                    break
        else:
            if self.current_command.done():
                self.current_command.update(self)
                self.current_command = None

    def physics_update(self, dt):
        pass

    def behaviour_update(self, dt):
        pass

    def command(self, command, *args, **kwargs):
        self.command_queue.add(lambda command: command(self, *args, **kwargs))

    def render(self, dt):
        pass

    def update(self, dt):
        self.rect.center = self.pos
        self.control(dt)
        self.command_update(dt)
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
