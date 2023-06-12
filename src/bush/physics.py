"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

import pygame

from bush import collision, util

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
        try:
            rects[type].union_ip(sprite.rect)
        except AttributeError:
            rects[type] = sprite.rect.copy()
        groups[type].add(sprite)
    for key in (TYPE_STATIC,):
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
        new_sprite.physics_data = PhysicsData(key, group)
        group.add(new_sprite)


def dynamic_update(self, dt, stop_on_collision=False):
    for axis in range(2):
        self.pos[axis] += self.velocity[axis] * dt
        self.update_rects()
        callbacks = (
            static_collision,
            dynamic_collision,
            trigger_collision,
        )
        for sprite in self.physics_data.collision_group:
            callbacks[sprite.physics_data.type](self, sprite, axis, stop_on_collision)


def static_collision(dynamic, static, axis, stop_on_collision):
    velocity = pygame.Vector2()
    velocity[axis] = -dynamic.velocity[axis]
    velocities = [velocity]
    if not velocity:
        velocity[axis] = 1
        velocities = [velocity, -velocity]
    motions = {}
    start_pos = tuple(dynamic.pos)
    for velocity in velocities:
        if velocity.length_squared() < 0.0001:
            continue
        velocity.scale_to_length(0.2)
        motion = pygame.Vector2()
        while collision.collide_rect_mask(
            dynamic.collision_rect, static.mask, static.rect.topleft
        ):
            dynamic.pos += velocity
            motion += velocity
            dynamic.update_rects()
        motions[motion.length_squared()] = motion
        dynamic.pos.update(start_pos)
        dynamic.update_rects()
    if motions:
        dynamic.pos += motions[min(motions.keys())]


def dynamic_collision(dynamic1, dynamic2, axis, stop_on_collision):
    # TODO
    pass


def trigger_collision(dynamic, trigger, axis, stop_on_collision):
    # TODO
    if collision.collide_rect_mask(
        dynamic.collision_rect.move(-trigger.rect.left, -trigger.rect.top), trigger.mask
    ):
        trigger.on_collision(dynamic)
