"""
player - class for the player
"""
from typing import Union

import pygame

import environment
from bush import entity_component, event_binding, physics, util


class Player(environment.EnvironmentSprite):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(self, pos, layer, map_env, engine, **__):
        rect = pygame.Rect(0, 0, 14, 14)
        rect.center = pos
        super().__init__(
            pos,
            util.rect_surf(rect, "blue"),
            engine,
            map_env,
            physics.PhysicsData(physics.TYPE_DYNAMIC, pygame.sprite.Group()),
            id="player",
            layer=layer,
        )
        self.rect = rect
        self.rect.center = self.pos
        self.engine = engine
        entity_component.prepare_health(self, 12, 12, self.kill)
        self.heal = lambda amount: entity_component.heal(self, amount)
        self.hurt = lambda amount: entity_component.hurt(self, amount)
        self.walk_speed = 64
        self.run_speed = 96
        self.current_mana = 6
        self.mana_capacity = 12
        self.save_state = self.engine.state
        self.save_fields = (
            "current_mana",
            "mana_capacity",
            "current_health",
            "health_capacity",
        )
        self.load_data()

    def save_data(self):
        for field in self.save_fields:
            self.save_state.set(field, getattr(self, field), "player")

    def load_data(self):
        try:
            for field in self.save_fields:
                setattr(self, self.save_state.get(field, "player"))
        except KeyError:
            self.save_data()

    def event(self, event):
        if event.type == event_binding.BOUND_EVENT:
            self.command(event.name)

    def command(self, command_name):
        words = command_name.split(" ")
        if words[0] == "walk":
            directions = {
                "up": (self.desired_velocity.x, -self.walk_speed),
                "down": (self.desired_velocity.x, self.walk_speed),
                "left": (-self.walk_speed, self.desired_velocity.y),
                "right": (self.walk_speed, self.desired_velocity.y),
            }
            self.speed = self.walk_speed
            self.desired_velocity = pygame.Vector2(directions[words[1]])
        if words[0] == "run":
            directions = {
                "up": (0, -self.run_speed),
                "down": (0, self.run_speed),
                "left": (-self.run_speed, 0),
                "right": (self.run_speed, 0),
            }
            self.speed = self.run_speed
            self.desired_velocity = pygame.Vector2(directions[words[1]])
        if words[0] == "stop":
            directions = {
                "up": (self.desired_velocity.x, 0),
                "down": (self.desired_velocity.x, 0),
                "left": (0, self.desired_velocity.y),
                "right": (0, self.desired_velocity.y),
            }
            self.desired_velocity = pygame.Vector2(directions[words[1]])
        if self.desired_velocity:
            self.desired_velocity.scale_to_length(self.speed)

    def change_collision_group(self, collision_group):
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)

    def change_layer(self, layer):
        self._layer = layer

    def update(self, dt):
        self.current_mana = min(self.current_mana + (dt * 0.1), self.mana_capacity)
        super().update(dt)
