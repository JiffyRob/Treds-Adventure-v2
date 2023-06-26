import pygame


class WeatherCycle:
    def __init__(self, size):
        self.surface = pygame.Surface(size).convert()
        self.min_brightness, self.max_brightness = 0.0, 128.0
        self.brightness_increment = 0
        self.brightness = 255
        # all units are milliseconds
        self.time = 0
        self.time_of_day = 0
        self.day_length = 10_000
        self.night_length = 7_000
        self.transition_length = 2_000

        self.start = pygame.time.get_ticks()
        self.last_frame_time = self.start

        self.transition_offset = 4_500
        self.enabled = True

    def get_date(self):
        return (self.time // (self.day_length + self.night_length)) + 1

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def update(self, dt):
        self.time += pygame.time.get_ticks() - self.last_frame_time
        self.time_of_day = self.time % (self.day_length + self.night_length)
        day_diff = self.time_of_day - self.day_length
        if day_diff <= 0:
            # it is daytime
            # set brightness based on distance from the night point
            # y=mx+b anyone?
            self.brightness = (
                ((self.max_brightness - self.min_brightness) / -self.transition_offset)
                * day_diff
            ) + self.min_brightness
            self.brightness = min(self.max_brightness, self.brightness)
        else:
            # it is night time
            night_diff = self.time_of_day - (self.day_length + self.night_length)
            # basically what happens for day but in reverse
            self.brightness = (
                ((self.min_brightness - self.max_brightness) / -self.transition_offset)
                * night_diff
            ) + self.max_brightness
            self.brightness = max(self.min_brightness, self.brightness)
        self.last_frame_time = pygame.time.get_ticks()
        if not self.enabled:
            self.brightness = self.max_brightness

    def render(self, surface: pygame.Surface):
        # invert brightness over itself in order to subtract darkness
        avg_brightness = (self.min_brightness + self.max_brightness) / 2
        darkness = round(((avg_brightness - self.brightness) * 2) + self.brightness)
        print(darkness)
        self.surface.fill((darkness, darkness, darkness))
        surface.blit(self.surface, (0, 0), special_flags=pygame.BLEND_SUB)

    def is_day(self):
        return self.brightness < (self.min_brightness + self.max_brightness) / 2
