"""
player - class for the player
"""
from typing import Union

import pygame

from bush import color, entity, physics, util


class Player(entity.Entity):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(self, pos: Union[pygame.Vector2, list, tuple], collision_group):
        super().__init__(util.circle_surf(6, color.RED, 1), pos, ())
        self.speed = 64
        rect = pygame.Rect(0, 0, 32, 32)
        rect.center = pos
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)
        self.image = util.rect_surf(rect, color.BLUE)
        self.rect = rect
        self.rect.center = self.pos

    def physics_update(self, dt):
        physics.dynamic_update(self, dt)

    def control(self, dt):
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
