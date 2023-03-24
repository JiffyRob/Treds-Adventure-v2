import pygame

import game_object
from bush import physics


class StaticNPC(game_object.StaticGameObject):
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
        **kwargs,
    ):
        super().__init__(pos, surface, engine, groups, topleft, None, id, layer, script)
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, None)
        self.mask = pygame.mask.from_surface(self.image)
        # TODO


class DynamicNPC(game_object.DynamicGameObject):
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
        collision_group=None,
        **kwargs,
    ):
        anim_dict = None
        if anim_name is not None:
            anim_dict = game_object.get_anim_dict(
                "npcs/" + anim_name, ((16, 32), (16, 16))[gnome]
            )
        super().__init__(
            pos,
            surface,
            engine,
            physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group),
            groups=groups,
            topleft=topleft,
            anim_dict=anim_dict,
            id=id,
            layer=layer,
            script=script,
        )
        self.mask = pygame.mask.from_surface(self.image)
        # TODO
