"""
player - class for the player
"""
from typing import Union

import pygame

from bush import entity, util, color, physics


class Player(entity.Entity):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(self, pos: Union[pygame.Vector2, list, tuple], map_size, body_group):
        super().__init__(util.circle_surf(6, color.RED, 1), pos, ())
        self.speed = 5
        self.map_rect = pygame.Rect(0, 0, *map_size)
        self.body = physics.Body(
            pos=self.pos,
            mass=10,
            shapes=[physics.Poly.as_circle(6, (0, 0))],
            group=body_group,
            type=physics.TYPE_DYNAMIC,
            friction=3,
            dynamic_collision_hook=self.collide,
        )

    def input(self, dt):
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

    def physics_update(self, dt):
        self.body.velocity = self.velocity
        self.body.update(dt)
        self.pos = self.body.pos
        self.velocity = pygame.Vector2()
        self.rect.center = self.pos

    def limit(self, dt):
        difference = max(self.map_rect.top - self.rect.top, 0)
        self.pos.y += difference
        difference = min(self.map_rect.bottom - self.rect.bottom, 0)
        self.pos.y += difference
        difference = max(self.map_rect.left - self.rect.left, 0)
        self.pos.x += difference
        difference = min(self.map_rect.right - self.rect.right, 0)
        self.pos.x += difference
        self.rect.center = self.pos

    def collide(self, other):
        pass
