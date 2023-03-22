import pygame

import game_object


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
    ):
        super().__init__(pos, surface, engine, groups, topleft, id, layer, script)
        # TODO


class DynamicNPC(game_object.DynamicGameObject):
    # TODO
    pass
