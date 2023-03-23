import pygame

import scripts
from bush import entity, physics, sound_manager, timer, util

player = sound_manager.glob_player


class StaticGameObject(entity.Actor):
    def __init__(
        self,
        pos,
        surface,
        engine,
        groups=(),
        topleft=False,
        id=None,
        layer=None,
        script=None,
        entity_group=None,
        other_groups=None,
    ):
        super().__init__(pos, surface, groups, id, layer, topleft)
        # scripting
        self.script = scripts.get_script(
            script, self, engine, entity_group, other_groups
        )
        if self.script is not None:
            self.script.begin()
        # state
        self.facing = "down"
        self.state = "idle"
        self.pushed_state = None

    # scripting
    def update_script(self, dt):
        if self.script is not None:
            self.script.update(dt)

    # scripting commands
    def push_state(self, state):
        self.pushed_state = state

    @staticmethod
    def play_sound(name):
        player.play(name)

    @staticmethod
    def get_player():
        return player

    def spawn_particle(self, name, pos):
        # TODO
        print("spawning a particle", name, pos)

    def unload_script(self):
        self.script.end()
        self.script = None

    # state
    def update_state(self):
        if self.velocity:
            self.facing = util.string_direction(self.velocity)

    # engine
    def update(self, dt):
        # update script
        self.update_script(dt)
        # update state
        self.update_state()


class DynamicGameObject(StaticGameObject):
    def __init__(
        self,
        pos,
        surface,
        engine,
        environment,
        physics_data,
        weight=10,
        speed=72,
        groups=(),
        topleft=False,
        id=None,
        layer=None,
        start_health=12,
        max_health=12,
        on_death=None,
        script=None,
    ):
        super().__init__(pos, surface, engine, groups, topleft, id, layer, script)
        # motion
        self.desired_velocity = pygame.Vector2()
        self.weight = weight
        self.speed = speed
        self.environment = environment
        self.current_terrain = self.environment.environment_data("default")
        self.current_terrain_name = "default"
        self.physics_data = physics_data
        self.mask = pygame.Mask(self.rect.size, True)
        # health
        self.current_health = start_health
        self.health_capacity = max_health
        self.on_death = on_death
        if self.on_death is None:
            self.on_death = lambda: None
        self.poison_hurt_timer = timer.Timer(0)
        self.poison_stop_timer = timer.Timer(0)

    # scripting commands
    def move(self, direction):
        self.desired_velocity = direction

    def move_toward(self, dest):
        if (self.pos - dest).length_squared() > 0.5:
            self.desired_velocity = (dest - self.pos).scale_to_length(self.speed)

    def stop(self):
        self.desired_velocity *= 0

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
        physics.dynamic_update(self, dt, sliding)
        # update health
        self.update_health()
        # update state
        super().update(dt)
