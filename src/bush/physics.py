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


def dynamic_update(self, dt, stop_on_collision=False):
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
            if not self.velocity[ind]:
                continue
            callbacks[sprite.physics_data.type](self, sprite, ind, stop_on_collision)


def rect_mask_collide(rect, mask):
    rect_mask = pygame.Mask(rect.size, True)
    value = mask.overlap(rect_mask, rect.topleft) is not None
    return value


def static_collision(dynamic, static, axis, stop_on_collision):
    # get direction of velocity on given axis
    velocity = pygame.Vector2()
    velocity[axis] = dynamic.velocity[axis] / abs(dynamic.velocity[axis])
    direction = -velocity
    # directions to try going
    walk_directions = (
        pygame.Vector2(-direction.y, direction.x),
        pygame.Vector2(direction.y, -direction.x),
        pygame.Vector2(direction) * 0.4,
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
    # return value
    collided = False
    # walk in all directions
    while rect_mask_collide(
        check_rect.move(-pygame.Vector2(static.rect.topleft)), static.mask
    ):
        collided = True
        walk_direction = walk_directions[direction_index]
        check_pos = start_pos + (walk_direction * distance)
        distance += 0.25
        direction_index = (direction_index + 1) % 3
        check_rect.center = check_pos
    dynamic.rect = check_rect
    dynamic.pos = pygame.Vector2(check_rect.center)
    if collided and stop_on_collision:
        dynamic.velocity[axis] = 0
    return collided


def dynamic_collision(dynamic1, dynamic2, dt, _):
    # TODO
    pass


def friction_collision(dynamic, friction, dt, _):
    # TODO
    pass


def trigger_collision(dynamic, trigger, dt, _):
    # TODO
    pass
