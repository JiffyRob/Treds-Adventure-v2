import itertools

import pygame


class Animation:
    def __init__(self, images, length=250):
        self.lengths = length
        if isinstance(length, int):
            lengths = [length for _ in images]
        self.images = list(images)
        self.index = 0
        self.last_start_time = 0

    def increment(self):
        self.index += 1
        self.index %= len(self.images)

    def image(self):
        now = pygame.time.get_ticks()
        if now - self.last_start_time > self.lengths[self.index]:
            self.increment()
        return self.images[self.index]


class PingPongAnimation(Animation):
    def __init__(self, images, length=250):
        super().__init__(images, length)
        self.direction = 1

    def increment(self):
        self.index += self.direction
        if not (0 <= self.index < len(self.images)):
            self.direction *= -1
            self.index += self.direction * 2


class OnceAnimation(Animation):
    def increment(self):
        self.index = min(self.index + 1, len(self.images) - 1)
