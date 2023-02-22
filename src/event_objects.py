import pygame

from bush import entity, physics


class Teleport(entity.Entity):
    def __init__(
        self,
        *,
        pos,
        engine,
        collision_group,
        width=16,
        height=16,
        dest,
        dest_map=None,
        groups=(),
        **_
    ):
        super().__init__(pos, groups=groups, layer=1276)
        self.dest = pygame.Vector2([int(i) for i in dest.split(", ")])
        self.dest_map = dest_map or engine.current_map
        self.engine = engine
        self.physics_data = physics.PhysicsData(physics.TYPE_TRIGGER, collision_group)
        self.rect.size = (width, height)
        self.rect.topleft = pos
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, collided, axis):
        if collided == self.engine.player:
            if self.engine.current_map != self.dest_map:
                self.engine.load_map(self.dest_map, self.dest)
            else:
                self.engine.player.pos = self.dest
