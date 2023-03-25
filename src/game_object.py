import pygame

import environment
import scripts
from bush import animation, asset_handler, entity, physics, sound_manager, timer, util

player = sound_manager.glob_player
loader = asset_handler.AssetHandler("resources/sprites")


class StaticGameObject(entity.Actor):
    def __init__(
        self,
        pos,
        surface,
        engine,
        groups=(),
        topleft=False,
        anim_dict=None,
        id=None,
        layer=None,
        script=None,
        interaction_script=None,
        event_group=None,
    ):
        super().__init__(pos, surface, groups, id, layer, topleft)
        # scripting
        self.engine = engine
        self.script = scripts.get_script(script, self, engine, event_group)
        if self.script is not None:
            self.script.begin()
        self.interaction_script = scripts.get_script(
            interaction_script, self, engine, event_group
        )
        # state
        self.facing = "down"
        self.state = "idle"
        self.pushed_state = None
        self.anim_dict = anim_dict

    # scripting
    def update_script(self, dt):
        if self.script is not None:
            self.script.update(dt)
        if self.interaction_script is not None:
            self.interaction_script.update(dt)
            if self.interaction_script.complete:
                self.script.unpause()
                self.interaction_script.reset()

    def interact(self):
        if self.interaction_script is not None:
            self.interaction_script.begin()
            if self.script is not None:
                self.script.pause()

    # scripting commands
    def push_state(self, state):
        self.pushed_state = state

    def unpush_state(self):
        self.pushed_state = None

    @staticmethod
    def play_sound(name):
        player.play(name)

    @staticmethod
    def get_sound_player():
        return player

    def spawn_particle(self, name, pos):
        # TODO
        print("spawning a particle", name, pos)

    def unload_script(self):
        self.script.end()
        self.script = None

    # state
    def update_state(self):
        if self.pushed_state:
            self.state = self.pushed_state
        else:
            self.state = None

    # rendering
    def update_image(self):
        if self.anim_dict:
            self.anim = self.anim_dict.get(
                f"{self.state} {self.facing}",
                self.anim_dict.get(
                    f"{self.state} {util.round_string_direction(self.facing)}",
                    self.anim_dict.get(self.state, None),
                ),
            )
        if self.anim is not None:
            self.image = self.anim.image()

    # engine
    def update(self, dt):
        # update script
        self.update_script(dt)
        # update state
        self.update_state()
        # update image
        self.update_image()


class DynamicGameObject(StaticGameObject):
    def __init__(
        self,
        pos,
        surface,
        engine,
        physics_data,
        weight=10,
        speed=48,
        groups=(),
        map_env=None,
        topleft=False,
        anim_dict=None,
        id=None,
        layer=None,
        start_health=12,
        max_health=12,
        on_death=None,
        script=None,
        interaction_script=None,
        event_group=None,
    ):
        super().__init__(
            pos,
            surface,
            engine,
            groups,
            topleft,
            anim_dict,
            id,
            layer,
            script,
            interaction_script,
            event_group,
        )
        # motion
        self.desired_velocity = pygame.Vector2()
        self.desired_position = None
        self.weight = weight
        self.speed = speed
        self.environment = map_env
        if self.environment is not None:
            self.current_terrain = self.environment.environment_data("default")
        else:
            self.current_terrain = environment.EnvironmentData(
                **environment.DEFAULT_DATA
            )
        self.current_terrain_name = "default"
        self.physics_data = physics_data
        self.collision_rect = self.rect
        self.mask = pygame.Mask(self.rect.size, fill=True)
        # health
        self.current_health = start_health
        self.health_capacity = max_health
        self.on_death = on_death
        if self.on_death is None:
            self.on_death = lambda: None
        self.poison_hurt_timer = timer.Timer(0)
        self.poison_stop_timer = timer.Timer(0)

    # scripting commands
    def interact(self):
        self.face(self.engine.player.pos)
        super().interact()

    def move(self, direction):
        self.desired_velocity = direction

    def move_toward(self, dest):
        if (self.pos - dest).length_squared() > 0.5:
            self.desired_velocity = (dest - self.pos).scale_to_length(self.speed)

    def move_to(self, dest):
        self.desired_position = dest

    def stop(self, force=False):
        self.desired_velocity *= 0
        # here are two fun ways to avoid branching!
        self.velocity *= not force
        self.desired_position = (None, self.desired_position)[force]

    def face(self, pos):
        self.stop(True)
        self.facing = util.round_string_direction(util.string_direction(pos - self.pos))

    def terrain_allows_move(self, move):
        return move in self.current_terrain.moves

    def update_terrain(self):
        if self.environment is None:
            return
        self.current_terrain_name = self.environment.get_environment_at(
            self.mask, self.rect.topleft
        )
        self.current_terrain = self.environment.environment_data(
            self.current_terrain_name
        )

    def update_rects(self):
        self.rect.center = self.pos
        self.collision_rect.center = self.pos

    def change_environment(self, new_env):
        self.environment = new_env

    def heal(self, amount):
        self.current_health = min(self.current_health + amount, self.health_capacity)

    def hurt(self, amount):
        self.current_health = max(self.current_health - amount, 0)

    def poison(self, amount=1, length=20000, interval=3500):
        self.poison_hurt_timer = timer.Timer(interval, lambda: self.hurt(amount), True)
        self.poison_stop_timer = timer.Timer(length, self.end_poison)

    def end_poison(self):
        self.poison_hurt_timer = timer.Timer(0)
        self.poison_stop_timer = timer.Timer(0)

    def update_health(self):
        # take care of poison
        self.poison_hurt_timer.update()
        self.poison_stop_timer.update()
        # reclamp health in case poison screwed it up
        self.current_health = pygame.math.clamp(
            self.current_health, 0, self.health_capacity
        )
        # DIE
        if self.current_health == 0:
            self.on_death()

    def update_state(self):
        if self.velocity:
            self.state = self.current_terrain.move_state
            self.facing = util.string_direction(self.velocity)
        else:
            self.state = self.current_terrain.idle_state

    def update(self, dt):
        # calculate and update self.current_terrain
        self.update_terrain()
        # go to desired position
        if self.desired_position is not None:
            self.move_toward(self.desired_position)
        # modify speed
        if self.desired_velocity:
            self.desired_velocity.scale_to_length(
                self.speed * self.current_terrain.speed
            )
        # slippety-slide!
        if self.current_terrain.traction != 1:
            sliding = True
            self.velocity += self.desired_velocity * self.current_terrain.traction
        else:
            sliding = False
            self.velocity = self.desired_velocity
        # physics update
        self.update_rects()
        physics.dynamic_update(self, dt, sliding)
        self.update_rects()
        # update health
        self.update_health()
        # update state
        super().update(dt)


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
