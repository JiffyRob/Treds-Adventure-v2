import os

import globals
from bush import effect, physics
from game_objects import base


class BaseObstacle(base.GameObject):
    """Does nothing.  Damage to be implemented later."""

    registry_groups = ("main", "collision", "attackable", "scriptable")

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
    registry_groups = ("main", "collision", "attackable", "scriptable")

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
        self.updating = True

    def kill(self):
        self.drawable = False
        self.updating = False

    def update(self, dt):
        if self.updating:
            super().update(dt)

    def update_state(self, dt):
        super().update_state(dt)
        if globals.player.collision_rect.colliderect(self.collision_rect):
            globals.player.hurt(self.touch_damage)

    def reload(self):
        self.respawn()
        self.drawable = True
        self.updating = True
        self.update_rects()
        self.visual_effects.clear()


def get_anim_dict(path, size):
    return base.get_anim_dict(os.path.join("enemies", path), size)
