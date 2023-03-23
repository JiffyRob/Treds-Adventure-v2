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
        id=None,
        layer=None,
        script=None,
        **kwargs,
    ):
        super().__init__(pos, surface, engine, groups, topleft, None, id, layer, script)
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, None)
        self.mask = pygame.mask.from_surface(self.image)
        # TODO
