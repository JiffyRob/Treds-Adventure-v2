import pygame

from bush import entity, level, asset_handler, physics, util

loader = asset_handler.glob_loader
TREE_MASK = pygame.mask.from_surface(
    loader.load("resources/tiles/trees.png").subsurface((0, 0, 32, 64))
)


class Tree(entity.Entity):
    def __init__(self, pos, image, collision_group=None, *_, layer=5, **__):
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        self.mask = TREE_MASK.copy()
        super().__init__(pos, image, layer=layer)


class Bush(entity.Entity):
    pass


class Sign(entity.Entity):
    pass
