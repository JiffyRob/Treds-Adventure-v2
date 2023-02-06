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
        "grip",
        "traction",
    ),
)
TERRAIN_DATA = loader.load("data/terrain.json")
DEFAULT_DATA = TERRAIN_DATA["default"]
TERRAIN_ORDER = TERRAIN_DATA.pop("order")
for key, value in TERRAIN_DATA.items():
    TERRAIN_DATA[key] = EnvironmentData(**{**value, **DEFAULT_DATA})


class EnvironmentHandler:
    def __init__(self, tiles, tile_size=(16, 16)):
        self.tiles = tiles
        self.tile_size = tile_size

    def get_environment_at(self, rect):
        # TODO
        return "default"

    def environment_data(self, environment):
        return TERRAIN_DATA.get(environment, "default")


class EnvironmentSprite(entity.Actor):
    def __init__(
        self,
        pos,
        surface,
        engine,
        environment,
        physics_data,
        weight=10,
        speed=72,
        groups=(),
        id=None,
        layer=None,
    ):
        super().__init__(pos, surface, groups, id, layer)
        self.facing = "down"
        self.state = "idle"
        self.desired_velocity = pygame.Vector2()
        self.weight = weight
        self.speed = speed
        self.environment = environment
        self.current_terrain = self.environment.environment_data("default")
        self.current_terrain_name = "default"
        self.physics_data = physics_data
        self.engine = engine

    def terrain_allows_move(self, move):
        return move in self.current_terrain.moves

    def update_state(self):
        if self.velocity:
            self.state = self.current_terrain.move_state
            self.facing = util.string_direction(self.velocity)
        else:
            self.state = self.current_terrain.idle_state

    def update_terrain(self):
        self.current_terrain_name = self.environment.get_environment_at(self.rect)
        self.current_terrain = self.environment.environment_data(
            self.current_terrain_name
        )

    def update(self, dt):
        # calculate and update self.current_terrain
        self.update_terrain()
        # modify speed
        if self.desired_velocity:
            self.desired_velocity.scale_to_length(
                self.speed * self.current_terrain.speed
            )
        # slippety-slide!
        if self.current_terrain.traction != 1:
            sliding = True
            self.velocity += self.desired_velocity * self.current_terrain.traction
        else:
            sliding = False
            self.velocity = self.desired_velocity
        # physics update
        physics.dynamic_update(self, dt, sliding)
        # update state
        self.update_state()
        print(self.velocity, self.desired_velocity)
