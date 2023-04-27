import pygame

from bush import asset_handler, autotile, collision, entity, physics, util, util_load
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


def green_farmplant(*args, **kwargs):
    return FarmPlant("green", *args, **kwargs)


def orange_farmplant(*args, **kwargs):
    return FarmPlant("orange", *args, **kwargs)


class FarmPlant(entity.Entity):
    def __init__(
        self,
        color,
        pos,
        surface,
        collision_group=None,
        layer=5,
        farmplants_orange_group=None,
        farmplants_green_group=None,
        id=None,
        *_,
        **__
    ):
        self.color = color
        self.physics_data = physics.PhysicsData(physics.TYPE_STATIC, collision_group)
        super().__init__(pos, surface, layer=layer, id=id)
        self.mask = pygame.mask.from_surface(surface)
        self.autotile = autotile.BinaryAutotile(self.get_neighbors)
        self.farmplants_group = {
            "orange": farmplants_orange_group,
            "green": farmplants_green_group,
        }[self.color]

    def get_neighbors(self):
        positions = {
            tuple(self.pos + (0, -16)): autotile.NORTH,
            tuple(self.pos + (16, 0)): autotile.EAST,
            tuple(self.pos + (0, 16)): autotile.SOUTH,
            tuple(self.pos + (-16, 0)): autotile.WEST,
        }
        neighbors = {
            autotile.NORTHWEST: False,
            autotile.NORTHEAST: False,
            autotile.SOUTHEAST: False,
            autotile.SOUTHWEST: False,
        }
        for sprite in self.farmplants_group:
            pos = tuple(sprite.pos)
            direction = positions.get(pos, None)
            if direction is not None:
                neighbors[direction] = True
        return neighbors

    def update(self, dt):
        super().update(dt)
        self.image = FARMPLANT_IMAGES[self.color][self.autotile.calculate()]


class Throwable(base.StaticGameObject):
    def __init__(
        self,
        pos,
        surface,
        engine,
        layer=5,
        id=None,
        groups=(),
        main_group=None,
        *_,
        **__
    ):
        super().__init__(pos, surface, engine, groups, True, id=id, layer=layer)
        self.state = STATE_GROUND
        self.velocity = pygame.Vector2()
        self.dest_height = None
        self.accum_height = 0
        self.speed = 400
        self.weight = 10
        self.main_group = main_group

    def pick_up(self):
        if self.state == STATE_GROUND:
            self.state = STATE_HELD
            self.engine.player.carrying = self

    def throw(self):
        self.speed = 250
        self.weight = 15
        self.accum_height = 0
        self.state = STATE_THROWN
        self.engine.player.carrying = None
        self.velocity = (
            util.string_direction_to_vec(self.engine.player.facing) * self.speed
        )
        self.dest_height = self.engine.player.rect.bottom - self.rect.bottom
        self.dest_height += self.engine.player.rect.height
        if self.velocity.y > 0:
            self.dest_height += 5

    def position(self):
        self.pos.update(self.engine.player.rect.midtop)

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
            for sprite in self.main_group.sprites():
                if collision.collides(self.rect, sprite.rect) and sprite not in {
                    self.engine.player,
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
            return
            self.kill()
