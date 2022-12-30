import random

import pygame


def seek(actor, target):
    desired_velocity = (target.pos - actor.pos).normalize() * actor.speed
    steering = desired_velocity - actor.velocity
    if steering.length() > actor.max_steering_force:
        steering.scale_to_length(actor.max_steering_force)
    return steering


def seek_arrival(actor, target):
    distance = actor.pos.distance_to(target.pos)
    if distance > actor.arrival_distance:
        return seek(actor, target)
    desired_velocity = (
        (target.pos - actor.pos).normalize()
        * actor.speed
        * distance
        / actor.arrival_distance
    )
    steering = desired_velocity - actor.velocity
    if steering.length() > actor.max_steering_force:
        steering.scale_to_length(actor.max_steering_force)


def pursue(actor, target):
    t = actor.pos.distance_to(target.pos) / actor.speed
    return seek(target.pos + (target.velocity * t))


def flee(actor, target):
    desired_velocity = -(target.pos - actor.pos).normalize() * actor.speed
    steering = desired_velocity - actor.velocity
    if steering.length() > actor.max_steering_force:
        steering.scale_to_length(actor.max_steering_force)
    actor.velocity += steering


def evade(actor, target):
    t = actor.pos.distance_to(target.pos) / actor.speed
    return flee(target.pos + (target.velocity * t))


def wander(actor):
    displacement = pygame.Vector2(actor.wander_power).rotate(random.randint(0, 360))
    actor.velocity += displacement
