import pygame
from bush import animation, physics, util

import globals
from game_objects import base


class Chest(base.GameObject):
    registry_groups = ("main", "collision", "interactable")

    def __init__(self, data):
        anim_dict = {
            "open": animation.Animation((base.load_tile(7),)),
            "closed": animation.Animation((base.load_tile(6),)),
        }
        super().__init__(
            data,
            anim_dict=anim_dict,
            physics_data=physics.PhysicsData(
                physics.TYPE_STATIC, data.registry.get_group("collision")
            ),
            initial_state="closed",
        )
        self.item = data.misc.get("item", None)
        self.mask = pygame.Mask(self.rect.size, True)

    def interact(self):
        if util.direction(globals.player.pos - self.pos)[1] > 0:
            if self.state == "closed":
                self.state = "open"
                if self.item:
                    globals.engine.dialog(f"Obtained {self.item}")
                    globals.player.get(self.item)

                else:
                    globals.engine.dialog("The chest is empty")


class Pickup(base.GameObject):
    registry_groups = ("main", "physics")

    def __init__(self, data):
        super().__init__(
            data,
            physics_data=physics.PhysicsData(
                physics.TYPE_TRIGGER, data.registry.get("physics")
            ),
        )
        self.thing = data.misc.get("thing")

    def on_collision(self, collided):
        if collided is globals.player:
            globals.player.get(self.thing)
            self.kill()
