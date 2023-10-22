import globals
from bush import timer


class Inator:
    """Base tool class.  All Tools must follow the Doofenschmirtz class naming convention"""

    def __init__(self, usage_delay=250, push_state=None, mana_cost=0):
        self.use_timer = timer.Timer(usage_delay)
        self.use_timer.finish()
        self.push_state = push_state
        self.mana_cost = 0

    def equip(self):
        self.use_timer.finish()

    def dequip(self):
        pass

    def can_be_used(self):
        return self.use_timer.done() and globals.player.current_mana >= self.mana_cost

    def use(self):
        globals.player.current_mana -= self.mana_cost
        if self.can_be_used():
            self.use_callback()
            if self.push_state is not None:
                globals.player.push_state(self.push_state)

    def use_callback(self):
        print(self, "used")


def interaction_rect_collide(player, sprite):
    return player.get_interaction_rect().colliderect(sprite.collision_rect)
