import random

import pygame

from scripts import base


class RandomWalkScript(base.EntityScript):
    def __init__(self, sprite, engine):
        super().__init__(sprite, engine)

    def update(self, dt):
        super().update()
        self.go_direction(
            self.sprite.desired_velocity
            + pygame.Vector2(6, 6).rotate(random.random() * 360)
        )
