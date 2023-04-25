import pygame

import scripts
from bush import animation, asset_handler, entity, physics, util

loader = asset_handler.AssetHandler(
    asset_handler.join(asset_handler.glob_loader.base, "sprites")
)


class GameObject(entity.Actor):
    def __init__(
        self,
        pos,
        engine,
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
        self.engine = engine
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
        return self.engine.player

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
        self.script_queue.append(
            scripts.get_script(script_name, self, self.engine, self.entity_group)
        )
        self.script_queue[-1].begin()

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
            if self.script_queue[-1].complete:
                self.script_queue = self.script_queue[:-1]
                self.script_queue[-1].unpause()

    def update_rects(self):
        self.rect.center = self.pos

    def update(self, dt):
        self.update_script(dt)
        self.update_state(dt)
        self.update_physics(dt)
        self.update_image(dt)
        super().update(dt)


class MobileGameObject(GameObject):
    def __init__(
        self,
        pos,
        engine,
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
            engine,
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

    def update_rects(self):
        self.collision_rect.center = self.pos
        self.rect.center = self.pos

    def get_anim_key(self):
        return f"{self.state} {self.facing}"

    def update_physics(self, dt):
        self.velocity = self.desired_velocity  # TODO: add environment
        physics.dynamic_update(self, dt)
        self.update_rects()


def get_anim_dict(path, size):
    frames = loader.load(
        path + ".png", loader=asset_handler.load_spritesheet, frame_size=size
    )
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
