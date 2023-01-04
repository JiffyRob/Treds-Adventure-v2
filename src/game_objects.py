import pygame

from bush import color, entity, physics, util


class Block(entity.Entity):
    def __init__(self, pos):
        surface = util.rect_surf((0, 0, 32, 32), color.GREEN)
        super().__init__(surface, pos)
        self.body = physics.StaticBody(pygame.Mask((32, 32), True), (64, 64))

    def physics_update(self, dt):
        physics.entity_update(self, dt)
