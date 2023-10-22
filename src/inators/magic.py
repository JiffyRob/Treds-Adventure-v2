import random

import pygame

import globals
from game_objects import arg
from game_objects.projectiles import magic
from inators import base


class SpellInator(base.Inator):  # TODO: make amulets that run SNEK scripts
    def __init__(self):
        super().__init__(2000, mana_cost=15)

    def use_callback(self):
        half_size = globals.engine.screen_size / 2
        for i in range(15):
            magic.Lightening(
                arg.GameObjectArgs(
                    globals.player.pos
                    + (
                        random.randint(-half_size[0], half_size[0]),
                        random.randint(-half_size[1], half_size[1]),
                    ),
                    globals.player.registry,
                    layer=1000,
                )
            )
