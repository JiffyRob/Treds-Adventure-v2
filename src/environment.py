from collections import namedtuple

import pygame

from bush import asset_handler, entity, physics, util

loader = asset_handler.glob_loader
EnvironmentData = namedtuple(
    "EnvironmentData",
    (
        "speed",
        "moves",
        "move_state",
        "idle_state",
        "needs",
        "min_exempt_weight",
        "consequence",
        "pitfall",
        "sound",
        "traction",
    ),
)
TERRAIN_DATA = loader.load("data/terrain.json")
DEFAULT_DATA = TERRAIN_DATA["default"]
TERRAIN_ORDER = TERRAIN_DATA.pop("order")
for key, value in TERRAIN_DATA.items():
    TERRAIN_DATA[key] = EnvironmentData(**{**DEFAULT_DATA, **value})
del key, value  # don't want those cluttering up the namespace


class EnvironmentHandler:
    def __init__(self, env_masks=None):
        self.env_masks = env_masks or {}
        self.empty_mask = pygame.Mask((0, 0))

    def get_environment_at(self, mask, offset=(0, 0)):
        for key in TERRAIN_ORDER:
            if self.env_masks.get(key, self.empty_mask).overlap(mask, offset):
                return key
        return "default"

    def environment_data(self, environment):
        return TERRAIN_DATA.get(environment, "default")
