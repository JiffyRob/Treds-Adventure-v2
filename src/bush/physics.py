"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

TYPE_STATIC = 0
TYPE_DYNAMIC = 1
TYPE_FRICTION = 2
TYPE_TRIGGER = 3

PhysicsData = namedtuple("PhysicsData", ("type", "collision_group"))


def dynamic_update(self, dt):
    self.pos += self.velocity * dt
    callbacks = (
        static_collision,
        dynamic_collision,
        friction_collision,
        trigger_collision,
    )
    for sprite in self.physics_data.collision_group:
        callbacks[sprite.physics_data.type](self, sprite, dt)


def static_collision(dynamic, static, dt):
    # TODO
    pass


def dynamic_collision(dynamic1, dynamic2, dt):
    # TODO
    pass


def friction_collision(dynamic, friction, dt):
    # TODO
    pass


def trigger_collision(dynamic, trigger, dt):
    # TODO
    pass
