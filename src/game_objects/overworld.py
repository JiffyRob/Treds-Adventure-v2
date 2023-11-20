import random

import globals
import particle_util
from bush import collision, particle, util
from game_objects import base

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
        self.accum_height = 0
        self.speed = 400
        self.weight = 10
        self.particle = data.misc.get("particle", "grass")

    def kill(self):
        frames = particle_util.load(self.particle, (12, 13))
        globals.engine.spawn_particles(
            [
                particle.ImageParticle(
                    util.randinrect(self.rect),
                    util.randincircle(164),
                    random.choice(frames),
                    is_alive=particle.DurationCallback(0.2),
                )
                for _ in range(10)
            ]
        )
        super().kill()

    def interact(self):
        if globals.player.pick_up(self):
            self.pos = globals.player.pos
            self.pos3.z = globals.player.rect.height - 16
            self.state = STATE_HELD

    def throw(self):
        self.speed = 250
        self.weight = 15
        self.state = STATE_THROWN
        globals.player.carrying = None
        self.velocity.xy = (
            util.string_direction_to_vec(globals.player.facing) * self.speed
        )
        self.velocity.z = self.speed / 6

    def update(self, dt):
        super().update(dt)
        if self.state == STATE_THROWN:
            self.velocity += (0, 0, -self.weight)
            self.velocity.scale_to_length(self.speed)
            veloc = self.velocity * dt
            self.pos3 += veloc
            if self.pos3.z <= 0:
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
                            self.kill()

    def limit(self, map_rect):
        if not map_rect.contains(self.rect):
            self.kill()


class Sign(Throwable):
    registry_groups = ("main", "interactable")

    def __init__(self, data):
        data.misc["particle"] = data.misc.get("particle", "woodbreak")
        super().__init__(data)
        self.text = data.script

    def interact(self):
        if util.direction(globals.player.pos - self.pos)[1] > 0:
            globals.engine.dialog(self.text)
        else:
            super().interact()


class Cow(base.GameObject):
    registry_groups = ("main", "interactable")

    def interact(self):
        globals.engine.dialog("Moooooo.")
