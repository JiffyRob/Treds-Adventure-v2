import pygame

import globals
from bush import entity, physics


class Teleport(entity.Entity):
    registry_groups = ("main", "collision", "teleports")

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
        if "return_pos" in data.misc:
            self.return_pos = pygame.Vector2(
                [int(i) for i in data.misc["retrun_pos"].split(", ")]
            )
        else:
            self.return_pos = self.rect.center + pygame.Vector2(0, 12)
            self.pos_relative = True
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
        self.linked_teleport = data.misc.get("entrance", None)
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
            old_state = globals.engine.stack.pop()  # remove the currently loaded map
            state = globals.engine.stack.get_current()  # we need the map below
            if self.linked_teleport is None:
                self.linked_teleport = old_state.filename.split(".")[0]
            state = globals.engine.stack.get_current()
            state.reload_map()
            group = state.registry.get_group("teleports")
            teleport = group.get_by_id(self.linked_teleport)
            globals.player.reset(
                teleport.return_pos,
                state.map_properties.get("player_layer", 4),
                state.registry,
                state.map_properties.get("tiny", False),
            )
            globals.player.on_teleport()
