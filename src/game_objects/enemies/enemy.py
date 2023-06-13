import os

from bush import physics
from game_objects import base


class BaseObstacle(base.GameObject):
    """Does nothing.  Damage to be implemented later."""

    groups = (
        "main",
        "collision",
    )

    def __init__(
        self,
        pos,
        registry,
        surface=None,
        anim_dict=None,
        id=None,
        layer=None,
        topleft=False,
        initial_state=None,
        physics_data=None,
        start_health=1,
        max_health=1,
    ):
        super().__init__(
            pos,
            registry,
            surface=surface,
            anim_dict=anim_dict,
            id=id,
            layer=layer,
            topleft=topleft,
            initial_state=initial_state,
            physics_data=physics_data,
            start_health=start_health,
            max_health=max_health,
        )


class BaseEnemy(base.MobileGameObject):
    """Runs a script.  Damage and such to be implemented later"""

    groups = ("main", "collision", "attackable")

    def __init__(
        self,
        pos,
        registry,
        surface=None,
        anim_dict=None,
        id=None,
        layer=None,
        topleft=False,
        initial_state=None,
        start_health=1,
        max_health=1,
        script=None,
        speed=36,
        touch_damage=2,
        **kwargs,
    ):
        super().__init__(
            pos,
            registry,
            surface=surface,
            anim_dict=anim_dict,
            id=id,
            layer=layer,
            topleft=topleft,
            initial_state=initial_state,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, registry.get_group("collision")
            ),
            start_health=start_health,
            max_health=max_health,
        )
        self.speed = speed
        self.touch_damage = touch_damage
        self.run_script(script)

    def update_state(self, dt):
        super().update_state(dt)
        if self.player.collision_rect.colliderect(self.collision_rect):
            self.player.hurt(self.touch_damage)


def get_anim_dict(path, size):
    return base.get_anim_dict(os.path.join("enemies", path), size)
