import itertools
import random

import pygame

import globals
import particle_util
from bush import animation, particle, timer, util


class WeatherCycle:
    WEATHERTYPE_DNCYCLE = 1  # do day/night cycle
    WEATHERTYPE_RAINY = 2  # add rain drops
    WEATHERTYPE_SNOWING = 4  # add falling snowflakes
    WEATHERTYPE_FOGGY = 8  # add fog
    WEATHERTYPE_DARK = 16  # add ambient blackness
    WEATHERTYPE_THUNDER = 32  # add random blinks of light

    def __init__(self, size):
        self.rect = pygame.Rect((0, 0), size)
        self.above_rect = pygame.Rect(0, 0, self.rect.width, 1)
        self.below_rect = pygame.Rect(
            0, self.rect.height * 0.25, self.rect.width, self.rect.height * 0.75
        )
        self.surface = pygame.Surface(size).convert()
        self.fog_surface = pygame.Surface(size).convert()
        self.fog_surface.set_colorkey("chartreuse")

        # dn cycle
        self.min_brightness, self.max_brightness = 0.0, 128.0
        self.brightness_increment = 0
        self.brightness = 255
        self.time = 0  # all units are milliseconds
        self.time_of_day = 0
        self.day_length = 10_000
        self.night_length = 7_000
        self.transition_length = 2_000
        self.transition_offset = 4_500

        # thunder
        self.thunder_lengths = (
            4_000,
            100,
            400,
            100,
        )  # time off, time on, time off, time on
        self.thunder_cycle = itertools.cycle(self.thunder_lengths)
        self.thunder_timer = timer.DTimer(
            next(self.thunder_cycle), on_finish=self.thunder_step
        )
        self.thundering = False

        # fog
        self.fog_anim = animation.Animation(
            [
                util.repeat(pygame.transform.scale_by(img, 2), self.rect.size)
                for img in particle_util.load("fog", (16, 16))
            ]
        )

        # basic weather setup
        self.weathertype = self.WEATHERTYPE_DNCYCLE
        self.manager = particle.ParticleManager()

    def get_date(self):
        return (self.time // (self.day_length + self.night_length)) + 1

    def update(self, dt):
        self.time += dt * 1000
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
        # cancel day night cycle (calculation still done above)
        if not self.weathertype & self.WEATHERTYPE_DNCYCLE:
            self.brightness = self.max_brightness
        # rain drops
        if self.weathertype & self.WEATHERTYPE_RAINY:
            drop_frames = particle_util.load("raindrop", (8, 8))
            self.manager.add(
                [
                    particle.ImageParticle(
                        util.randinrect(self.rect),
                        pygame.Vector2(-64, 96),
                        random.choice(drop_frames),
                        particle.DurationCallback(random.random() * 1.2),
                    )
                    for _ in range(round(200 * dt))
                ]
            )
            self.brightness = max(64, self.brightness - 32)
        # snowflakes
        if self.weathertype & self.WEATHERTYPE_SNOWING:
            frames = particle_util.load("snow", (32, 32))
            self.manager.add(
                [
                    particle.ImageParticle(
                        util.randinrect(self.rect),
                        pygame.Vector2(-32, 64),
                        random.choice(frames),
                        particle.DurationCallback(random.random() * 1.2),
                    )
                    for _ in range(round(100 * dt))
                ]
            )
            self.brightness = min(self.max_brightness, self.brightness + 32)

        # thunder
        if self.weathertype & self.WEATHERTYPE_THUNDER:
            self.thunder_timer.update(dt)
            self.brightness = max(64, self.brightness - 48)
        self.manager.update(dt)

    def set_weather(self, weather=WEATHERTYPE_DNCYCLE):
        self.manager.kill()
        self.thundering = False
        self.thunder_cycle = itertools.cycle(self.thunder_lengths)
        self.thunder_timer = timer.DTimer(
            next(self.thunder_cycle), on_finish=self.thunder_step
        )
        self.weathertype = weather

    def thunder_step(self):
        print("step", self.thundering)
        self.thundering = not self.thundering
        self.thunder_timer = timer.DTimer(next(self.thunder_cycle), self.thunder_step)

    def render(self, surface: pygame.Surface):
        self.manager.draw(surface)
        # invert brightness over itself in order to subtract darkness
        avg_brightness = (self.min_brightness + self.max_brightness) / 2
        darkness = round(((avg_brightness - self.brightness) * 2) + self.brightness)
        if not self.thundering:
            self.surface.fill((darkness, darkness, darkness))
        else:
            self.surface.fill((15, 30, 128))
        surface.blit(self.surface, (0, 0), special_flags=pygame.BLEND_SUB)
        if self.weathertype & self.WEATHERTYPE_FOGGY:
            surface.blit(self.fog_anim.image(), (0, 0), special_flags=pygame.BLEND_MULT)
        if self.weathertype & self.WEATHERTYPE_DARK:
            pos = (
                globals.player.pos
                + util.string_direction_to_vec(globals.player.facing) * 24
            )
            self.fog_surface.fill(globals.engine.bgcolor)
            pygame.draw.circle(self.fog_surface, "chartreuse", pos, 64)
            surface.blit(self.fog_surface, (0, 0))

    def is_day(self):
        return self.brightness < (self.min_brightness + self.max_brightness) / 2
