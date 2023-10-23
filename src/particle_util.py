import math
import random
from itertools import cycle

import pygame

from bush import asset_handler, particle, util

loader = asset_handler.AssetHandler("particles")
FIREBALL_FRAMES = None
SMOKE_FRAMES = None


def init():
    global FIREBALL_FRAMES
    global SMOKE_FRAMES
    global loader
    FIREBALL_FRAMES = loader.load_spritesheet("fireball.png")
    SMOKE_FRAMES = loader.load_spritesheet("smoke.png", (32, 32))


def load(name, size=None):
    if size is None:
        return loader.load(name + ".png")
    return loader.load_spritesheet(name + ".png", size)


def explosion(
    pos,
    manager,
    size=16,
    ring=True,
    soot=True,
    cloud=True,
    fireball=True,
):
    particles = []
    # flying ring
    if size > 5 and ring:
        particles.append(
            particle.CircleParticle(
                pos,
                (0, 0),
                int(size / 2) + 1,
                "white",
                size // 2,
                256,
                particle.DurationCallback(2.5),
            )
        )
    # soot balls
    if soot:
        for i in range(size**2 // 30):
            offset = util.randincircle(size)
            while not offset:
                offset = util.randincircle(size)
            particles.append(
                particle.CircleParticle(
                    pos + offset,
                    offset.normalize() * (128 + (random.random() * 32 * size)),
                    3,
                    "black",
                    is_alive=particle.on_rect_callback(
                        (0, 0, 1000, 1000)
                    ),  # TODO: use screen rect
                )
            )
    # explosion cloud
    # don't ask how this works, I'm not entirely sure either
    if cloud:
        spacing = int(size / 36) + 1
        layers = int(size / spacing) + 1
        shrink_speed = (
            10  # lower this to speed up the rate at which the explosion shrinks
        )
        max_time = (layers * shrink_speed) + 20
        clouds = []
        for i in range(0, layers):
            radius = i * spacing
            for _ in range(int((radius**2 * math.pi) / (32**2)) + 1):
                offset = util.randincircle(radius, True) + pygame.Vector2(-16, -16)
                clouds.append(
                    particle.AnimParticle(
                        pos + offset,
                        0,
                        particle.AnimData(
                            iter(SMOKE_FRAMES), max(50, max_time - (shrink_speed * i))
                        ),
                    )
                )
        clouds.reverse()
        particles.extend(clouds)
        radius = 4
        for i in range(size // 4):
            offset = util.randincircle(radius, True) + pygame.Vector2(-16, -16)
            particles.append(
                particle.AnimParticle(
                    pos + offset, 0, particle.AnimData(iter(SMOKE_FRAMES), 150)
                )
            )
    # duh duh duh duh-duh duh -- FIREBALL!
    if fireball:
        for _ in range(size**2 // 100):
            offset = util.randincircle(size)
            particles.append(
                particle.AnimParticle(
                    pos + offset,
                    offset.normalize() * size * 6,
                    particle.AnimData(cycle(FIREBALL_FRAMES), 250),
                    particle.DurationCallback(1),
                )
            )
    manager.add(particles)
