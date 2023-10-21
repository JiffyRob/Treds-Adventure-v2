import pygame

import globals
from bush import timer
from game_objects import arg
from game_objects.projectiles import bomb


class Inator:
    """ "Base tool class.  All Tools must follow the Doofenschmirtz class naming convention"""

    def __init__(self, player, usage_delay=250, push_state=None, mana_cost=0):
        self.player = player
        self.use_timer = timer.Timer(usage_delay)
        self.use_timer.finish()
        self.push_state = push_state
        self.mana_cost = 0

    def equip(self):
        self.use_timer.finish()

    def dequip(self):
        pass

    def can_be_used(self):
        return self.use_timer.done() and self.player.current_mana >= self.mana_cost

    def use(self):
        if self.can_be_used():
            self.use_callback()
            if self.push_state is not None:
                self.player.push_state(self.push_state)

    def use_callback(self):
        print(self, "used")


class Whackinator(Inator):
    """Known as a 'Sword' to some heathens"""

    def __init__(self, player):
        super().__init__(player)


class Boominator(Inator):
    """Goes boom"""

    def can_be_used(self):
        return super().can_be_used() and globals.player.has("bomb")

    def use_callback(self):
        bomb.Bomb(arg.from_projectile_shooter(self.player, pygame.Vector2()))
        globals.player.lose("bomb")


def get_tool(player, tool_id):
    if tool_id in TOOL_DICT:
        return TOOL_DICT[tool_id](player)
    print(f"Warning: tool_id {tool_id!r} not found.  Using Null Inator instead")
    return Inator(player)


TOOL_DICT = {"base": Inator, "Whackinator": Whackinator, "bomb": Boominator}
