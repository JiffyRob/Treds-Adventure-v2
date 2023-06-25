import os

from bush import effect, physics
from game_objects import base


class BaseObstacle(base.GameObject):
    """Does nothing.  Damage to be implemented later."""

    registry_groups = (
        "main",
        "collision",
        "attackable",
    )

    def __init__(
        self,
        data,
        initial_state="idle",
        physics_data=None,
        start_health=1,
        max_health=1,
    ):
        super().__init__(
            data=data,
            initial_state=initial_state,
            physics_data=physics_data,
            start_health=start_health,
            max_health=max_health,
        )


class BaseEnemy(base.MobileGameObject):
    """Runs a script.  Damage and such to be implemented later"""

    registry_groups = ("main", "collision", "attackable")

    def __init__(
        self,
        data,
        anim_dict=None,
        initial_state=None,
        start_health=1,
        max_health=1,
        script=None,
        speed=36,
        touch_damage=2,
    ):
        super().__init__(
            data=data,
            anim_dict=anim_dict,
            initial_state=initial_state,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, data.registry.get_group("collision")
            ),
            start_health=start_health,
            max_health=max_health,
            hit_effect=effect.Blink(500),
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
