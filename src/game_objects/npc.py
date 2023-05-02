import sys

import pygame

import globals
from bush import physics, util
from game_objects import base


class StaticNPC(base.GameObject):
    groups = (
        "main",
        "collision",
        "event",
        "interactable",
    )

    def __init__(
        self,
        pos,
        registry,
        surface,
        topleft=False,
        id=None,
        layer=None,
        script=None,
        interaction_script=None,
        **kwargs,
    ):
        super().__init__(
            pos,
            registry,
            surface,
            id=id,
            layer=layer,
            topleft=topleft,
        )
        self.physics_data = physics.PhysicsData(
            physics.TYPE_STATIC, registry.get_group("collision")
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = script
        self.interaction_script = interaction_script
        if self.normal_script:
            self.run_script(self.normal_script)

    def interact(self):
        self.run_script(self.interaction_script)


class DynamicNPC(base.MobileGameObject):
    groups = ("main", "collision", "event", "interactable")

    def __init__(
        self,
        pos,
        registry,
        surface,
        topleft=False,
        anim_name=None,
        gnome=False,  # gnomes are smaller
        id=None,
        layer=None,
        script=None,
        interaction_script=None,
        **kwargs,
    ):
        anim_dict = None
        if anim_name is not None:
            anim_dict = base.get_anim_dict(
                "npcs/" + anim_name, ((16, 32), (16, 16))[gnome]
            )
        super().__init__(
            pos,
            registry,
            surface,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, registry.get_group("collision")
            ),
            topleft=topleft,
            anim_dict=anim_dict,
            id=id,
            layer=layer,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = script
        self.interaction_script = interaction_script
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
