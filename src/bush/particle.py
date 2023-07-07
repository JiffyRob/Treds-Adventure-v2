from collections import namedtuple

import pygame

AnimData = namedtuple("AnimData", ("frames", "delay"))


class AnimParticle:
    def __init__(
        self, pos, velocity, anim, is_alive=lambda self, dt: not self.anim_done
    ):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity)

        self.frames = anim.frames
        self.delay = anim.delay / 1000
        self.image = next(self.frames)
        self.age = 0
        self.anim_done = False
        self.is_alive = is_alive
        self.rect = pygame.Rect(self.pos, self.image.get_size())

    def update(self, dt):
        self.pos += self.vel * dt
        self.age += dt
        if not self.anim_done and self.age >= self.delay:
            self.age = 0
            try:
                self.image = next(self.frames)
            except StopIteration:
                self.anim_done = True
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        return self.is_alive(self, dt)


class ImageParticle:
    def __init__(self, pos, velocity, image, is_alive=lambda self, dt: True):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.image = image
        self.is_alive = is_alive

    def update(self, dt):
        self.pos += self.velocity * dt
        return self.is_alive(self, dt)


class RectParticle:
    cached_images = {}

    def __init__(self, pos, velocity, size, color, is_alive=lambda self, dt: True):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)

        self.size = tuple(size)
        self.color = color
        self.image = None
        self.is_alive = is_alive
        self.update_image()  # self.image set here

    def update(self, dt):
        self.pos += self.velocity * dt
        return self.is_alive(self, dt)

    def update_image(self):
        cache_lookup = (self.size, self.color)

        cached_image = self.cached_images.get(cache_lookup, None)

        if not cached_image:
            cached_image = pygame.Surface((self.size[0], 3 * self.size[1]))
            cached_image.fill(self.color)

            self.cached_images[cache_lookup] = cached_image

        self.image = cached_image


class CircleParticle:
    cached_images = {}

    def __init__(
        self,
        pos,
        velocity,
        radius,
        color,
        width=0,
        expansion=0,
        is_alive=lambda self, dt: self.radius > 0,
    ):
        self.true_pos = pygame.Vector2(pos)
        self.pos = self.true_pos - (radius, radius)
        self.rect = (self.true_pos, (radius, radius))
        self.velocity = pygame.Vector2(velocity)
        self.radius = radius
        self.color = color
        self.image = None
        self.width = width
        self.expansion = expansion
        self.is_alive = is_alive
        self.update_image()  # self.image set here

    def update(self, dt):
        self.true_pos += self.velocity * dt
        if self.expansion:
            self.radius += self.expansion * dt
            self.update_image()
        self.pos = self.true_pos - (self.radius, self.radius)
        self.rect = (self.true_pos, (self.radius, self.radius))
        return self.is_alive(self, dt)

    def update_image(self):
        # use a rounded radius because sub-pixel doesn't happen and else caching will be almost useless
        radius = round(self.radius)

        cache_lookup = (radius, self.color, self.width)

        cached_image = self.cached_images.get(cache_lookup, None)

        if not cached_image:
            cached_image = pygame.Surface((radius * 2, radius * 2))
            cached_image.fill((0, 255, 255))
            cached_image.set_colorkey((0, 255, 255))
            pygame.draw.circle(
                cached_image, self.color, (radius, radius), radius, self.width
            )

            self.cached_images[cache_lookup] = cached_image

        self.image = cached_image


class ParticleManager:
    def __init__(self):
        self.particles = []

    def update(self, dt):
        self.particles = [
            particle for particle in self.particles if particle.update(dt)
        ]

    def add(self, particles):
        self.particles.extend(particles)

    def kill(self):
        self.particles = []

    def draw(self, surface, offset=(0, 0)):
        surface.fblits(
            [(particle.image, particle.pos + offset) for particle in self.particles]
        )

    def __len__(self):
        return len(self.particles)


class DurationCallback:
    def __init__(self, duration, on_finish=lambda *args, **kwargs: None):
        self.duration = duration
        self.on_finish = on_finish

    def __call__(self, particle, dt):
        self.duration = max(0, self.duration - dt)
        if not self.duration:
            self.on_finish(particle, dt)
            return 0
        return 1


def on_rect_callback(rect):
    def on_rect(particle, dt):
        return pygame.Rect(rect).colliderect(particle.rect)

    return on_rect
