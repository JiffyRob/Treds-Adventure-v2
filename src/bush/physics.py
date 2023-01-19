"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

import pygame

TYPE_STATIC = 0
TYPE_DYNAMIC = 1
TYPE_FRICTION = 2
TYPE_TRIGGER = 3

PhysicsData = namedtuple("PhysicsData", ("type", "collision_group"))


def dynamic_update(self, dt):
    for ind, axis in enumerate(("x", "y")):
        if not self.velocity[ind]:
            continue
        self.pos[ind] += self.velocity[ind] * dt
        callbacks = (
            static_collision,
            dynamic_collision,
            friction_collision,
            trigger_collision,
        )
        for sprite in self.physics_data.collision_group:
            callbacks[sprite.physics_data.type](self, sprite, ind)


def rect_mask_collide(rect, mask):
    rect_mask = pygame.Mask(rect.size, True)
    value = mask.overlap(rect_mask, rect.topleft) is not None
    if value:
        print("bang!")
    return value


def static_collision(dynamic, static, axis):
    # get direction of velocity on given axis
    velocity = pygame.Vector2()
    velocity[axis] = dynamic.velocity[axis] / abs(dynamic.velocity[axis])
    direction = -velocity
    # directions to try going
    walk_directions = (
        pygame.Vector2(-direction.y, direction.x),
        pygame.Vector2(direction.y, -direction.x),
        pygame.Vector2(direction),
    )
    # start position of entity
    start_pos = pygame.Vector2(dynamic.pos)
    # position to check
    check_pos = pygame.Vector2(start_pos)
    # how long to walk in each direction
    distance = 1
    # which direction to walk in
    direction_index = 0
    # rect to check collision from
    check_rect = dynamic.rect.copy()
    check_rect.center = check_pos
    # walk in all directions
    while rect_mask_collide(
        check_rect.move(-pygame.Vector2(static.rect.topleft)), static.mask
    ):
        walk_direction = walk_directions[direction_index]
        check_pos = start_pos + (walk_direction * distance)
        distance += 0.25
        direction_index = (direction_index + 1) % 3
        check_rect.center = check_pos
    dynamic.rect = check_rect
    dynamic.pos = pygame.Vector2(check_rect.center)


def dynamic_collision(dynamic1, dynamic2, dt):
    # TODO
    pass


def friction_collision(dynamic, friction, dt):
    # TODO
    pass


def trigger_collision(dynamic, trigger, dt):
    # TODO
    pass
