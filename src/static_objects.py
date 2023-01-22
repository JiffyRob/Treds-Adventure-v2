import pygame

from bush import asset_handler, entity, level, physics, util

loader = asset_handler.glob_loader
TREE_MASK = pygame.mask.from_surface(
    loader.load("resources/tiles/trees.png").subsurface((0, 0, 32, 64))
)


class Tree(entity.Entity):
    def __init__(self, pos, image, collision_group=None, *_, layer=5, **__):
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        self.mask = TREE_MASK.copy()
        super().__init__(pos, image, layer=layer)


class Throwable(entity.Entity):
    def __init__(self, pos, image, collision_group=None, *_, layer=5, **__):
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        super().__init__(
            pos, image, layer=layer - 1
        )  # below player, but above layer below player
        print(self.image.get_bounding_rect().size)
        self.mask = pygame.mask.from_surface(self.image)


class Sign(entity.Entity):
    pass
