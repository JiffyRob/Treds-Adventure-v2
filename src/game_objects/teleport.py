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
        if "dest" in data.misc:
            self.dest = pygame.Vector2([int(i) for i in data.misc["dest"].split(", ")])
        else:
            self.dest = None
        self.dest_map = data.misc.get("dest_map", False) or globals.engine.current_map
        self.registry = data.registry
        self.physics_data = physics.PhysicsData(
            physics.TYPE_TRIGGER, self.registry.get_group("collision")
        )
        self.rect.size = (data.misc["width"], data.misc["height"])
        self.rect.topleft = data.pos
        self.pos = pygame.Vector2(self.rect.center)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, collided, dt):
        if collided is globals.player:
            if globals.engine.current_map != self.dest_map:
                globals.engine.load_map(self.dest_map, self.dest)
            else:
                globals.player.pos = self.dest
            globals.player.on_teleport()


class Exit(entity.Entity):
    registry_groups = ("main", "collision")

    def __init__(self, data):
        super().__init__(
            data.pos,
            None,
            (data.registry.get_group(key) for key in self.registry_groups),
        )
        self.dest = None
        if "dest" in data.misc:
            self.dest = pygame.Vector2([int(i) for i in data.misc["dest"].split(", ")])
        self.registry = data.registry
        self.physics_data = physics.PhysicsData(
            physics.TYPE_TRIGGER, self.registry.get_group("physics")
        )
        self.rect.size = (data.misc["width"], data.misc["height"])
        self.rect.topleft = data.pos
        self.pos = pygame.Vector2(self.rect.center)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, collided, dt):
        if collided is globals.player:
            globals.engine.stack.pop()  # remove the currently loaded map
            state = globals.engine.stack.pop()  # remove the map below and reload it
            if ".world" in state.filename:
                globals.engine.load_world(state.filename, self.dest)
            else:
                globals.engine.load_map(state.filename, self.dest)
            globals.player.on_teleport()
