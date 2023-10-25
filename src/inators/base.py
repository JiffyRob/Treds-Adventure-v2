import logging

import globals
from bush import timer

logger = logging.getLogger(__name__)


class Inator:
    """Base tool class.  All Tools must follow the Doofenschmirtz class naming convention"""

    def __init__(self, usage_delay=250, push_state=None, mana_cost=0):
        self.use_timer = timer.Timer(usage_delay)
        self.use_timer.finish()
        self.push_state = push_state
        self.mana_cost = mana_cost

    def equip(self):
        self.use_timer.finish()

    def dequip(self):
        pass

    def can_be_used(self):
        return self.use_timer.done() and globals.player.current_mana >= self.mana_cost

    def use(self):
        if self.can_be_used():
            globals.player.current_mana -= self.mana_cost
            self.use_callback()
            if self.push_state is not None:
                globals.player.push_state(self.push_state)

    def use_callback(self):
        logger.warning("This tool does nothing")


def interaction_rect_collide(player, sprite):
    return player.get_interaction_rect().colliderect(sprite.collision_rect)
