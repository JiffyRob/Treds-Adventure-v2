"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

import pygame

from bush import collision

TYPE_STATIC = 0
TYPE_DYNAMIC = 1
TYPE_TRIGGER = 2

PhysicsData = namedtuple("PhysicsData", ("type", "collision_group"))


def optimize_for_physics(group):
    groups = (
        pygame.sprite.Group(),
        pygame.sprite.Group(),
        pygame.sprite.Group(),
    )
    rects = [None, None, None, None]
    for sprite in group.sprites():
        type = sprite.physics_data.type
        print(groups[type], type)
        try:
            rects[type].union_ip(sprite.rect)
        except AttributeError:
            rects[type] = sprite.rect.copy()
    for key in (TYPE_STATIC, TYPE_TRIGGER):
        if rects[key] is None:
            continue
        megamask = pygame.Mask(rects[key].size)
        for sprite in groups[key]:
            megamask.draw(sprite.mask, sprite.rect.topleft)
            group.remove(sprite)
        new_sprite = pygame.sprite.Sprite()
        new_sprite.rect = megamask.get_rect()
        new_sprite.pos = new_sprite.rect.center
        new_sprite.mask = megamask
        new_sprite.physics_data = PhysicsData(TYPE_STATIC, group)
        group.add(new_sprite)
    print("optoed!")


def dynamic_update(self, dt, stop_on_collision=False):
    for ind, axis in enumerate(("x", "y")):
        if not self.velocity[ind]:
            continue
        self.pos[ind] += self.velocity[ind] * dt
        callbacks = (
            static_collision,
            dynamic_collision,
            trigger_collision,
        )
        for sprite in self.physics_data.collision_group:
            if not self.velocity[ind]:
                continue

            callbacks[sprite.physics_data.type](self, sprite, ind, stop_on_collision)


def static_collision(dynamic, static, axis, stop_on_collision):
    # get direction of velocity on given axis
    velocity = pygame.Vector2()
    velocity[axis] = dynamic.velocity[axis] / abs(dynamic.velocity[axis])
    direction = -velocity
    # directions to try going
    walk_directions = (
        pygame.Vector2(-direction.y, direction.x),
        pygame.Vector2(direction.y, -direction.x),
        pygame.Vector2(direction) * 0.6,
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
    while collision.collide_rect_mask(
        check_rect.move(-pygame.Vector2(static.rect.topleft)), static.mask
    ):
        collided = True
        walk_direction = walk_directions[direction_index]
        check_pos = start_pos + (walk_direction * distance)
        distance += 0.25
        direction_index = (direction_index + 1) % 3
        check_rect.center = check_pos
    if collided:
        dynamic.rect = check_rect
        dynamic.pos = pygame.Vector2(check_rect.center)
    else:
        dynamic.pos = dynamic.rect.center = check_pos
    if collided and stop_on_collision:
        dynamic.velocity[axis] = 0
    return collided


def dynamic_collision(dynamic1, dynamic2, dt, _):
    # TODO
    pass


def trigger_collision(dynamic, trigger, axis, _):
    # TODO
    if collision.collide_rect_mask(
        dynamic.rect.move(-trigger.rect.left, -trigger.rect.top), trigger.mask
    ):
        trigger.on_collision(dynamic, axis)
