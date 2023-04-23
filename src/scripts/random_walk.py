import random

import pygame

from bush import timer
from scripts import base


class RandomWalkScript(base.EntityScript):
    def init(self):
        self.last_pos = self.sprite.pos
        self.switch_timer = timer.Timer(1200, self.switch_direc, repeat=True)
        self.stopped = False

    def begin(self):
        super().begin()
        self.add_timer(self.switch_timer)

    def pause(self):
        super().pause()
        self.sprite.stop()
        self.switch_timer.finish()

    def unpause(self):
        super().unpause()
        print("unpause")
        self.switch_timer.reset()
        self.switch_direc()

    def switch_direc(self):
        if random.random() < 0.9:
            self.sprite.move(
                pygame.Vector2(1, 0).rotate(
                    90 * random.choice((random.random() * 3, random.randint(0, 3)))
                )
            )
            self.stopped = False
        else:
            self.sprite.stop()
            self.stopped = True

    def script_update(self, dt):
        super().script_update(dt)
        if (
            not self.stopped
            and (self.last_pos - self.sprite.pos).length()
            < self.sprite.speed * dt * 0.5
        ):
            self.switch_timer.reset()
            self.switch_direc()
        self.last_pos = self.sprite.pos
