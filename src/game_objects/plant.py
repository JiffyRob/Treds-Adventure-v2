import pygame

import globals
from bush import asset_handler, collision, entity, physics, util, util_load
from game_objects import base

loader = asset_handler.glob_loader
TREE_MASK = pygame.mask.from_surface(
    loader.load("tiles/trees.png").subsurface((0, 0, 32, 64))
)
FARMPLANT_IMAGES = {
    "green": loader.load(
        "tiles/farmplant_green.png",
        loader=util_load.load_spritesheet,
        frame_size=(16, 16),
    ),
    "orange": loader.load(
        "tiles/farmplant_orange.png",
        loader=util_load.load_spritesheet,
        frame_size=(16, 16),
    ),
}

# bush states
STATE_GROUND = 0
STATE_HELD = 1
STATE_THROWN = 2


class Throwable(base.GameObject):
    registry_groups = (
        "main",
        "interactable",
    )

    def __init__(self, data):
        super().__init__(data)
        self.state = STATE_GROUND
        self.velocity = pygame.Vector2()
        self.dest_height = None
        self.accum_height = 0
        self.speed = 400
        self.weight = 10

    def interact(self):
        if globals.player.pick_up(self):
            self.state = STATE_HELD
            self.registry.get_group("interactable").remove(self)

    def throw(self):
        self.speed = 250
        self.weight = 15
        self.accum_height = 0
        self.state = STATE_THROWN
        globals.player.carrying = None
        self.velocity = util.string_direction_to_vec(globals.player.facing) * self.speed
        self.dest_height = globals.player.rect.bottom - self.rect.bottom
        self.dest_height += globals.player.rect.height
        if self.velocity.y > 0:
            self.dest_height += 5

    def position(self):
        self.pos.update(globals.player.rect.midtop)

    def update(self, dt):
        super().update(dt)
        if self.state == STATE_THROWN:
            self.velocity += (0, self.weight)
            self.velocity.scale_to_length(self.speed)
            veloc = self.velocity * dt
            self.pos += veloc
            self.accum_height += self.accum_height + (self.weight * dt)
            if self.accum_height >= self.dest_height:
                self.kill()
            for sprite in self.registry.get_group("main").sprites():
                if collision.collides(self.rect, sprite.rect) and sprite not in {
                    globals.player,
                    self,
                }:
                    if hasattr(sprite, "mask"):
                        if collision.collide_rect_mask(
                            self.rect, sprite.mask, sprite.rect.topleft
                        ):
                            print("smash")
                            self.kill()

    def limit(self, map_rect):
        if super().limit(map_rect):
            return  # TODO currently this part is always executed
            self.kill()
