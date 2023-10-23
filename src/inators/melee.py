import pygame

import globals
from inators import base


class Whackinator(base.Inator):
    """Known as a 'Stick' to some heathens.  You can whack things with it."""

    def __init__(self):
        super().__init__(200)

    def use_callback(self):
        whacked = pygame.sprite.spritecollide(
            globals.player, globals.player.registry.get_group("attackable"), False
        )
        for sprite in whacked:
            if sprite is not globals.player:
                sprite.hurt(1)
                sprite.knockback(globals.player.pos, 3)


class Swooshinator(base.Inator):
    """Kinda like a stick, but made of metal and has a blade on the end"""

    def __init__(self):
        super().__init__(100)  #

    def use_callback(self):
        whacked = pygame.sprite.spritecollide(
            globals.player, globals.player.registry.get_group("attackable"), False
        )
        for sprite in whacked:
            if sprite is not globals.player:
                sprite.hurt(1)
                sprite.knockback(globals.player.pos, 5)
