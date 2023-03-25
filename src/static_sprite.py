import pygame

from bush import asset_handler, autotile, entity, physics, util_load

loader = asset_handler.glob_loader
TREE_MASK = pygame.mask.from_surface(
    loader.load("resources/tiles/trees.png").subsurface((0, 0, 32, 64))
)
FARMPLANT_IMAGES = {
    "green": loader.load(
        "resources/tiles/farmplant_green.png",
        loader=util_load.load_spritesheet,
        frame_size=(16, 16),
    ),
    "orange": loader.load(
        "resources/tiles/farmplant_orange.png",
        loader=util_load.load_spritesheet,
        frame_size=(16, 16),
    ),
}


def green_farmplant(*args, **kwargs):
    return FarmPlant("green", *args, **kwargs)


def orange_farmplant(*args, **kwargs):
    return FarmPlant("orange", *args, **kwargs)


class Throwable(entity.Entity):
    def __init__(self, pos, image, collision_group=None, *_, layer=5, **__):
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        super().__init__(
            pos, image, layer=layer - 1
        )  # below player, but above layer below player
        self.mask = pygame.mask.from_surface(self.image)


class FarmPlant(entity.Entity):
    def __init__(
        self,
        color,
        pos,
        image,
        collision_group=None,
        layer=5,
        farmplants_orange_group=None,
        farmplants_green_group=None,
        id=None,
        *_,
        **__
    ):
        self.color = color
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        super().__init__(pos, image, layer=layer, id=id)
        self.mask = pygame.mask.from_surface(image)
        self.autotile = autotile.BinaryAutotile(self.get_neighbors)
        self.farmplants_group = {
            "orange": farmplants_orange_group,
            "green": farmplants_green_group,
        }[self.color]

    def get_neighbors(self):
        positions = {
            tuple(self.pos + (0, -16)): autotile.NORTH,
            tuple(self.pos + (16, 0)): autotile.EAST,
            tuple(self.pos + (0, 16)): autotile.SOUTH,
            tuple(self.pos + (-16, 0)): autotile.WEST,
        }
        neighbors = {
            autotile.NORTHWEST: False,
            autotile.NORTHEAST: False,
            autotile.SOUTHEAST: False,
            autotile.SOUTHWEST: False,
        }
        for sprite in self.farmplants_group:
            pos = tuple(sprite.pos)
            direction = positions.get(pos, None)
            if direction is not None:
                print(direction, "found", pos)
                neighbors[direction] = True
        return neighbors

    def update(self, dt):
        super().update(dt)
        self.image = FARMPLANT_IMAGES[self.color][self.autotile.calculate()]


class Sign(entity.Entity):
    pass
