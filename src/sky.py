import pygame

from bush import entity, timer


class Sky(entity.Entity):
    def __init__(self, size):
        self.increment_speed = 30
        self.min_darkness, self.max_darkness = self.darkness_range = 10, 120
        self.day_time = (
            0.2 * 60000
        )  # first operand is time in minutes, for easy changing
        self.night_time = 0.2 * 60000
        self.current_timer = timer.Timer(0, lambda x=None: None)
        self.current_increment = 0
        self.darkness = self.min_darkness
        self.current_timer = timer.Timer(self.day_time, self.start_night_transition)
        super().__init__(
            pygame.Rect((0, 0), size).center, pygame.Surface(size).convert()
        )

    def update(self, dt):
        self.image.fill((self.darkness, self.darkness * 0.8, self.darkness * 0.8))
        self.darkness += self.current_increment * dt
        if self.darkness < self.min_darkness:
            self.current_timer = timer.Timer(self.day_time, self.start_night_transition)
            self.current_increment = 0
            self.darkness = self.min_darkness
        if self.darkness > self.max_darkness:
            self.current_timer = timer.Timer(self.night_time, self.start_day_transition)
            self.current_increment = 0
            self.darkness = self.max_darkness
        self.current_timer.update()

    def render(self, surface):
        surface.blit(self.image, (0, 0), None, pygame.BLEND_SUB)

    def stabilize_lighting(self):
        self.current_increment = 0

    def start_day_transition(self):
        self.current_increment = -self.increment_speed

    def start_night_transition(self):
        self.current_increment = self.increment_speed

    def is_day(self):
        return self.darkness == self.min_darkness or self.current_increment > 0
