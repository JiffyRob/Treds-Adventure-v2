import pygame

import globals
from bush import entity, physics


class Teleport(entity.Entity):
    groups = ("main", "collision")

    def __init__(self, *, pos, registry, width=16, height=16, dest, dest_map=None, **_):
        super().__init__(pos, layer=1276)
        for group in self.groups:
            registry.get_group(group).add(self)
        self.dest = pygame.Vector2([int(i) for i in dest.split(", ")])
        self.dest_map = dest_map or globals.engine.current_map
        self.registry = registry
        self.physics_data = physics.PhysicsData(
            physics.TYPE_TRIGGER, self.registry.get_group("collision")
        )
        self.rect.size = (width, height)
        self.rect.topleft = pos
        self.pos = pygame.Vector2(self.rect.center)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, collided):
        if collided == globals.player:
            if globals.engine.current_map != self.dest_map:
                globals.engine.load_map(self.dest_map, self.dest)
            else:
                globals.player.pos = self.dest
            globals.player.on_teleport()
