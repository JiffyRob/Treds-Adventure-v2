import itertools

import pygame


class Animation:
    def __init__(self, images, length=250):
        self.lengths = length
        if isinstance(length, int):
            self.lengths = [length for _ in images]
            print(self.lengths)
        self.images = list(images)
        self.index = 0
        self.last_start_time = 0

    def increment(self):
        self.index += 1
        self.index %= len(self.images)
        self.last_start_time = pygame.time.get_ticks()

    def reset(self):
        self.index = 0
        self.last_start_time = pygame.time.get_ticks()

    def image(self):
        now = pygame.time.get_ticks()
        if now - self.last_start_time > self.lengths[self.index]:
            self.increment()
        return self.images[self.index]

    def done(self):
        return False


class PingPongAnimation(Animation):
    def __init__(self, images, length=250):
        super().__init__(images, length)
        self.direction = 1

    def reset(self):
        super().reset()
        self.direction = 1

    def increment(self):
        self.index += self.direction
        if not (0 <= self.index < len(self.images)):
            self.direction *= -1
            self.index += self.direction * 2
        self.last_start_time = pygame.time.get_ticks()


class OnceAnimation(Animation):
    def __init__(self, images, length=250):
        super().__init__(images, length)
        self.hit_end = False

    def reset(self):
        super().reset()
        self.hit_end = False

    def increment(self):
        self.index = self.index + 1
        max_index = len(self.images) - 1
        if self.index > max_index:
            self.hit_end = True
            self.index = max_index
        self.last_start_time = pygame.time.get_ticks()

    def done(self):
        return self.hit_end
