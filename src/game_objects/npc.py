import sys

import pygame

import globals
from bush import physics, util
from game_objects import base


class StaticNPC(base.GameObject):
    registry_groups = (
        "main",
        "collision",
        "event",
        "interactable",
    )

    def __init__(
        self,
        data,
    ):
        super().__init__(data)
        self.physics_data = physics.PhysicsData(
            physics.TYPE_STATIC, data.registry.get_group("collision")
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = data.script
        self.interaction_script = data.interaction_script
        if self.normal_script:
            self.run_script(self.normal_script)

    def interact(self):
        self.run_script(self.interaction_script)


class DynamicNPC(base.MobileGameObject):
    registry_groups = ("main", "collision", "event", "interactable")

    def __init__(
        self,
        data,
    ):
        anim_dict = None
        anim_name = data.misc.get("anim_name", None)
        gnome = data.misc.get("gnome", None)
        if anim_name is not None:
            anim_dict = base.get_anim_dict(
                "npcs/" + anim_name, ((16, 32), (16, 16))[gnome]
            )
        super().__init__(
            data,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, data.registry.get_group("collision")
            ),
            anim_dict=anim_dict,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = data.script
        self.interaction_script = data.interaction_script
        self.run_script(self.normal_script)
        self.speed = 24

    def interact(self):
        self.facing = util.round_string_direction(
            util.string_direction(globals.player.pos - self.pos),
            util.METHOD_COUNTERCLOCKWISE,
        )
        self.run_script(self.interaction_script)

    def get_anim_key(self):
        return f"{self.state} {self.facing}"
