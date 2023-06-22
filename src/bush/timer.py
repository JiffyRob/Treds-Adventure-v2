import pygame


class Timer:
    def __init__(self, amount=1000, on_finish=lambda: None, repeat=False):
        self.wait = amount
        self.start = pygame.time.get_ticks()
        self.on_finish = on_finish
        self.repeat = repeat
        self.ran_ending = False

    def __repr__(self):
        return f"<bush.Timer (start={self.start}, remaining={self.time_left()}>"

    def time_left(self):
        return max(self.wait - (pygame.time.get_ticks() - self.start), 0)

    def done(self):
        return self.time_left() == 0

    def reset(self):
        self.start = pygame.time.get_ticks()
        self.ran_ending = False

    def finish(self):
        self.start = (pygame.time.get_ticks() - self.wait) - 1

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start >= self.wait and not self.ran_ending:
            self.on_finish()
            if self.repeat:
                self.reset()
            else:
                self.ran_ending = True
