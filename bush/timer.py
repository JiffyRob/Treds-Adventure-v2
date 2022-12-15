import pygame


class Timer:
    def __init__(self, amount=1000, on_finish=lambda: None, repeat=False):
        self.wait = amount
        self.start = pygame.time.get_ticks()
        self.on_finish = on_finish
        self.repeat = repeat

    def time_left(self):
        return max(self.wait - (pygame.time.get_ticks() - self.start), 0)

    def restart(self):
        self.start = pygame.time.get_ticks()

    def finish(self):
        self.start = (pygame.time.get_ticks() - self.wait) - 1

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start >= self.wait:
            self.on_finish()
            if self.repeat:
                self.restart()
