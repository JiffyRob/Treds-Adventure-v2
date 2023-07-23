"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

import pygame

from bush import collision, util

TYPE_STATIC = 0
TYPE_DYNAMIC = 1
TYPE_TRIGGER = 2

MAX_SPEED = 5

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
    checked_velocity = pygame.Vector2()
    sprite_velocity = self.velocity.copy() * dt
    callbacks = (static_collision, dynamic_collision, trigger_collision)
    while checked_velocity != sprite_velocity:
        checked_velocity.move_towards_ip(sprite_velocity, MAX_SPEED)
        self.pos += checked_velocity
        self.update_rects()
        for sprite in self.physics_data.collision_group:
            callbacks[sprite.physics_data.type](self, sprite, stop_on_collision)


def static_collision(dynamic, static, stop_on_collision):
    searcher = util.search(dynamic.pos)
    while collision.collide_rect_mask(
        dynamic.collision_rect, static.mask, static.rect.topleft
    ):
        dynamic.pos = pygame.Vector2(next(searcher))
        dynamic.update_rects()


def dynamic_collision(dynamic1, dynamic2, stop_on_collision):
    # TODO
    pass


def trigger_collision(dynamic, trigger, stop_on_collision):
    # TODO
    if collision.collide_rect_mask(
        dynamic.collision_rect.move(-trigger.rect.left, -trigger.rect.top), trigger.mask
    ):
        trigger.on_collision(dynamic)
