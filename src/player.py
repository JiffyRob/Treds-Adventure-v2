"""
player - class for the player
"""
from typing import Union

import pygame

from bush import color, entity, event_binding, physics, util


class Player(entity.Actor):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(
        self,
        pos: Union[pygame.Vector2, list, tuple],
        collision_group,
        layer,
        id="Player",
    ):
        rect = pygame.Rect(0, 0, 14, 14)
        rect.center = pos
        super().__init__(pos, util.rect_surf(rect, color.BLUE), (), id, layer)
        self.speed = 96
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)
        self.rect = rect
        self.rect.center = self.pos

    def event(self, event):
        if event.type == event_binding.BOUND_EVENT:
            self.command(event.name)

    def command(self, command_name):
        words = command_name.split(" ")
        if words[0] == "walk":
            directions = {
                "up": (self.velocity.x, -self.speed),
                "down": (self.velocity.x, self.speed),
                "left": (-self.speed, self.velocity.y),
                "right": (self.speed, self.velocity.y),
            }
            self.velocity = pygame.Vector2(directions[words[1]])
        if words[0] == "stop":
            directions = {
                "up": (self.velocity.x, 0),
                "down": (self.velocity.x, 0),
                "left": (0, self.velocity.y),
                "right": (0, self.velocity.y),
            }
            self.velocity = pygame.Vector2(directions[words[1]])
        if self.velocity:
            self.velocity.scale_to_length(self.speed)

    def update(self, dt):
        physics.dynamic_update(self, dt)
