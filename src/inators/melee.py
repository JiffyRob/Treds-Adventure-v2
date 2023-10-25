import pygame

import globals
from bush import collision
from inators import base


class Whackinator(base.Inator):
    """Known as a 'Stick' to some heathens.  You can whack things with it."""

    def __init__(self):
        super().__init__(200)

    def use_callback(self):
        player_rect = globals.player.get_interaction_rect().inflate(-3, -3)
        for sprite in globals.player.registry.get_group("attackable"):
            if sprite is not globals.player and sprite.collision_rect.colliderect(
                player_rect
            ):
                sprite.hurt(1)
                sprite.knockback(globals.player.pos, 3)


class Swooshinator(base.Inator):
    """Kinda like a stick, but made of metal and has a blade on the end"""

    def __init__(self):
        super().__init__(100)  #

    def use_callback(self):
        player_rect = globals.player.get_interaction_rect()
        for sprite in globals.player.registry.get_group("attackable"):
            if sprite is not globals.player and sprite.collision_rect.colliderect(
                player_rect
            ):
                sprite.hurt(1)
                sprite.knockback(globals.player.pos, 3)
