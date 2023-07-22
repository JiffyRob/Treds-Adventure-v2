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
    return flee(actor, target.pos + (target.velocity * t))


def wander(actor, _):
    displacement = pygame.Vector2(actor.wander_power).rotate(random.randint(0, 360))
    actor.velocity += displacement


def wander_near(actor, target):
    wander(actor, target)
    seek(actor, target)


def stop(actor, _):
    actor.velocity += -actor.velocity.scale_to_length(actor.max_steering_force)


NEEDED_ATTRS = {
    "pos",  # position of the sprite as a vector
    "speed",  # moving speed of the sprite
    "max_steering_force",  # max steering force that can be applied to the sprite
    "arrival_distance",  # distance to start slowing down when going to a destination
    "velocity",  # velocity of the sprite.l
    "wander_power",  # how much a sprite can turn when wandering
}

BEHAVIOURS = {
    "seek": seek,
    "seek_arrival": seek_arrival,
    "pursue": pursue,
    "flee": flee,
    "evade": evade,
    "wander": wander,
    "stop": stop,
    "wander_near": wander_near,
}
