import pygame

from bush import asset_handler, entity, physics

loader = asset_handler.glob_loader

TERRAIN_DATA = loader.load("data/terrain.json")
TERRAIN_ORDER = TERRAIN_DATA.pop("order")


class Environment:
    def __init__(self, tiles, tile_size=(16, 16)):
        self.tiles = tiles
        self.tile_size = tile_size

    def get_environment_at(self, rect):
        # TODO
        return "default"


class EnvironmentSprite(entity.Actor):
    def __init__(
        self,
        pos,
        surface,
        environment,
        physics_data,
        weight=10,
        groups=(),
        id=None,
        layer=None,
    ):
        super().__init__(pos, surface, groups, id, layer)
        self.velocity = pygame.Vector2()
        self.desired_velocity = pygame.Vector2()
        self.weight = weight
        self.environment = environment
        self.physics_data = physics_data

    def update(self, dt):
        physics.dynamic_update(self, dt)
