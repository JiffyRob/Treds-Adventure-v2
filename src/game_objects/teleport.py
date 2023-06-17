import pygame

import globals
from bush import entity, physics


class Teleport(entity.Entity):
    registry_groups = ("main", "collision")

    def __init__(self, data):
        super().__init__(
            data.pos,
            None,
            (data.registry.get_group(key) for key in self.registry_groups),
            data.id,
            1000,
        )
        self.dest = pygame.Vector2([int(i) for i in data.misc["dest"].split(", ")])
        self.dest_map = data.misc["dest_map"] or globals.engine.current_map
        self.registry = data.registry
        self.physics_data = physics.PhysicsData(
            physics.TYPE_TRIGGER, self.registry.get_group("collision")
        )
        self.rect.size = (data.misc["width"], data.misc["height"])
        self.rect.topleft = data.pos
        self.pos = pygame.Vector2(self.rect.center)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, collided):
        if collided == globals.player:
            if globals.engine.current_map != self.dest_map:
                globals.engine.load_map(self.dest_map, self.dest)
            else:
                globals.player.pos = self.dest
            globals.player.on_teleport()
