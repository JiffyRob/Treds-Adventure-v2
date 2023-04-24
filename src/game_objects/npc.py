import pygame

from bush import physics
from game_objects import base


class StaticNPC(base.GameObject):
    def __init__(
        self,
        pos,
        surface,
        engine,
        groups=(),
        topleft=False,
        id=None,
        layer=None,
        script=None,
        interaction_script=None,
        entity_group=None,
        **kwargs,
    ):
        super().__init__(
            pos,
            engine,
            surface,
            groups=groups,
            id=id,
            layer=layer,
            topleft=topleft,
            entity_group=entity_group,
        )
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, None)
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = script
        self.interaction_script = interaction_script
        if self.normal_script:
            self.run_script(self.normal_script)

    def interact(self):
        self.run_script(self.interaction_script)


class DynamicNPC(base.GameObject):
    def __init__(
        self,
        pos,
        surface,
        engine,
        groups=(),
        topleft=False,
        anim_name=None,
        gnome=False,  # gnomes are smaller
        id=None,
        layer=None,
        script=None,
        interaction_script=None,
        collision_group=None,
        **kwargs,
    ):
        anim_dict = None
        if anim_name is not None:
            anim_dict = base.get_anim_dict(
                "npcs/" + anim_name, ((16, 32), (16, 16))[gnome]
            )
        super().__init__(
            pos,
            engine,
            surface,
            physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group),
            groups=groups,
            topleft=topleft,
            anim_dict=anim_dict,
            id=id,
            layer=layer,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.normal_script = script
        self.interaction_script = interaction_script
        self.run_script(self.normal_script)
        self.speed = 72
        # TODO
