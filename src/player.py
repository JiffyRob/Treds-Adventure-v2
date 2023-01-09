"""
player - class for the player
"""
from typing import Union

import pygame

from bush import color, entity, physics, util, event_binding


class Player(entity.Entity):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(
        self, pos: Union[pygame.Vector2, list, tuple], collision_group, id="Player"
    ):
        super().__init__(util.circle_surf(6, color.RED, 1), pos, (), id)
        self.speed = 96
        rect = pygame.Rect(0, 0, 32, 32)
        rect.center = pos
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)
        self.image = util.rect_surf(rect, color.BLUE)
        self.rect = rect
        self.rect.center = self.pos

    def event(self, event):
        if event.type == event_binding.BOUND_EVENT:
            words = event.name.split(" ")
            if words[0] == "walk":
                directions = {
                    "up": (self.velocity.x, -self.speed),
                    "down": (self.velocity.x, self.speed),
                    "left": (-self.speed, self.velocity.y),
                    "right": (self.speed, self.velocity.y),
                }
                self.velocity = pygame.Vector2(directions[words[1]])
                print(self.velocity)
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

    def physics_update(self, dt):
        physics.dynamic_update(self, dt)

    def control(self, dt):
        # self.input()
        pass

    def input(self):
        keys = pygame.key.get_pressed()
        self.velocity = pygame.Vector2()
        if keys[pygame.K_LEFT]:
            self.velocity.x -= 1
        if keys[pygame.K_RIGHT]:
            self.velocity.x += 1
        if keys[pygame.K_UP]:
            self.velocity.y -= 1
        if keys[pygame.K_DOWN]:
            self.velocity.y += 1
        if self.velocity:
            self.velocity.scale_to_length(self.speed)
