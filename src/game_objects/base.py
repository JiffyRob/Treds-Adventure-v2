import pygame

import environment
import globals
import scripts
from bush import animation, asset_handler, entity, physics, util

loader = asset_handler.AssetHandler(
    asset_handler.join(asset_handler.glob_loader.base, "sprites")
)
loader.cache_asset_handler(asset_handler.glob_loader)


class GameObject(entity.Actor):
    def __init__(
        self,
        pos,
        registry,
        surface=None,
        anim_dict=None,
        groups=(),
        id=None,
        layer=None,
        topleft=False,
        initial_state=None,
        entity_group=None,
        physics_data=None,
        start_health=1,
        max_health=1,
    ):
        super().__init__(pos, surface, groups, id, layer, topleft)
        self.registry = registry
        self.anim_dict = {}
        if anim_dict is not None:
            self.anim_dict = anim_dict
        if initial_state is not None:
            self.state = initial_state
        elif self.anim_dict:
            self.state = "idle"
        else:
            self.state = None
        self.entity_group = entity_group
        self.pushed_state = None
        self.script_queue = []
        if physics_data is not None:
            self.physics_data = physics_data
        else:
            self.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, pygame.sprite.Group()
            )
        self.current_health = start_health
        self.health_capacity = max_health
        self.desired_velocity = pygame.Vector2()
        self.move_state = "walk"
        self.idle_state = "idle"
        self.facing = "down"

    def get_anim_key(self):
        return self.state

    def heal(self, amount):
        self.current_health = min(self.health_capacity, self.current_health + amount)

    def hurt(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.kill()

    def move(self, direction):
        self.desired_velocity = direction

    def stop(self):
        self.desired_velocity *= 0

    @property
    def player(self):
        return globals.engine.player

    @property
    def current_script(self):
        if self.script_queue:
            return self.script_queue[-1]

    def run_script(self, script_name, queue=True):
        for script in self.script_queue:
            script.pause()
        if queue:
            for script in self.script_queue:
                script.pause()
        else:
            for script in self.script_queue:
                script.finish()
            self.script_queue = []
        self.script_queue.append(scripts.get_script(script_name, self, self.registry))

    def update_state(self, dt):
        if self.desired_velocity:
            if self.state == self.idle_state:
                self.state = self.move_state
            self.facing = util.round_string_direction(
                util.string_direction(self.desired_velocity)
            )
        if not self.desired_velocity and self.state == self.move_state:
            self.state = self.idle_state
        if self.pushed_state:
            self.state = self.pushed_state

    def update_image(self, dt):
        if self.anim_dict:
            self.anim = self.anim_dict[self.get_anim_key()]
        if self.anim:
            self.image = self.anim.image()

    def update_physics(self, dt):
        self.pos += self.velocity * dt
        self.update_rects()

    def update_script(self, dt):
        if self.script_queue:
            self.script_queue[-1].update(dt)
            if self.script_queue[-1].finished():
                self.script_queue = self.script_queue[:-1]
                if self.script_queue:
                    self.script_queue[-1].unpause()

    def update_rects(self):
        self.rect.center = self.pos

    def update(self, dt):
        self.update_state(dt)
        self.update_physics(dt)
        self.update_image(dt)
        self.update_script(dt)
        super().update(dt)


class MobileGameObject(GameObject):
    def __init__(
        self,
        pos,
        registry,
        surface=None,
        anim_dict=None,
        groups=(),
        id=None,
        layer=None,
        topleft=False,
        initial_state=None,
        entity_group=None,
        physics_data=None,
        start_health=1,
        max_health=1,
    ):
        super().__init__(
            pos,
            registry,
            surface,
            anim_dict,
            groups,
            id,
            layer,
            topleft,
            initial_state,
            entity_group,
            physics_data,
            start_health,
            max_health,
        )
        self.facing = "down"
        if physics_data is None:
            self.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, pygame.sprite.Group()
            )
        self.collision_rect = self.rect.copy()

    def get_current_environment(self):
        return environment.TERRAIN_DATA[
            self.registry.masks.collide_mask(
                pygame.Mask(self.collision_rect.size, True),
                self.collision_rect.topleft,
                *environment.TERRAIN_ORDER,
            )
            or "default"
        ]

    def update_rects(self):
        self.collision_rect.center = self.pos
        self.rect.center = self.pos

    def get_anim_key(self):
        return f"{self.state} {self.facing}"

    def update_physics(self, dt):
        terrain = self.get_current_environment()
        # slippety-slide!
        if terrain.traction != 1:
            self.velocity += (self.desired_velocity * terrain.speed) * terrain.traction
        else:
            self.velocity = self.desired_velocity * terrain.speed
        physics.dynamic_update(self, dt)
        self.update_rects()


def get_anim_dict(path, size):
    frames = loader.load_sprite_sheet(path + ".png", size)
    return {
        "walk down": animation.Animation(frames[0:16:4], 150),
        "walk up": animation.Animation(frames[1:17:4], 150),
        "walk left": animation.Animation(frames[2:18:4], 150),
        "walk right": animation.Animation(frames[3:18:4], 150),
        "idle down": animation.Animation(frames[0:1]),
        "idle up": animation.Animation(frames[1:2]),
        "idle left": animation.Animation(frames[2:3]),
        "idle right": animation.Animation(frames[3:4]),
    }