import pygame

from bush import entity, physics, timer


class Projectile(entity.Entity):
    registry_groups = (
        "main",
        "collision",
    )

    def __init__(
        self,
        data,
        duration=None,
    ):
        super().__init__(
            pos=data.pos,
            surface=data.surface,
            groups=(data.registry.get_group(i) for i in self.registry_groups),
            id=data.id,
            layer=data.layer,
            topleft=data.topleft,
        )
        self.registry = data.registry
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, self.registry.get_group("collision")
        )
        self.velocity = data.misc.get("fly_direction", pygame.Vector2(1, 0))
        self.collision_rect = self.rect.copy()
        self.life_timer = timer.DTimer(duration, on_finish=self.kill)
        self.life_timer.reset()

    def reload(self):
        self.kill(False)

    def update(self, dt):
        super().update(dt)
        physics.dynamic_update(self, dt)
        self.life_timer.update(dt)

    def update_rects(self):
        self.rect.center = self.pos
        self.collision_rect.center = self.pos

    def on_death(self):
        pass

    def kill(self, call_death=True):
        if call_death:
            self.on_death()
        super().kill()
