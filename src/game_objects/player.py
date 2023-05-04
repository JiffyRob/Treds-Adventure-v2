"""
player - class for the player
"""
import pygame

import globals
import tool
from bush import animation, asset_handler, event_binding, physics, util
from game_objects import base

SPEED_MEANDERING = 32
SPEED_WALKING = 128
SPEED_RUNNING = 140

loader = asset_handler.AssetHandler(
    asset_handler.join(asset_handler.glob_loader.base, "sprites/player")
)
loader.cache_asset_handler(asset_handler.glob_loader)


class Player(base.MobileGameObject):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    groups = (
        "main",
        "player",
    )

    def __init__(self, pos, layer, registry, **__):
        tiny_frames = loader.load_sprite_sheet("tiny.png", (16, 16))
        foot_frames = loader.load_sprite_sheet(
            "feet-default.png",
            (16, 32),
        )
        torso_frames = loader.load_sprite_sheet(
            "torso-default.png",
            (16, 32),
        )
        arm_frames = loader.load_sprite_sheet(
            "arms-default.png",
            (16, 32),
        )
        head_frames = loader.load_sprite_sheet(
            "head-default.png",
            (16, 32),
        )
        anim_dict = {
            "tiny walk down": animation.Animation(tiny_frames[0:16:4], 150),
            "tiny walk up": animation.Animation(tiny_frames[1:17:4], 150),
            "tiny walk left": animation.Animation(tiny_frames[2:18:4], 150),
            "tiny walk right": animation.Animation(tiny_frames[3:18:4], 150),
            "tiny idle down": animation.Animation(tiny_frames[0:1]),
            "tiny idle up": animation.Animation(tiny_frames[1:2]),
            "tiny idle left": animation.Animation(tiny_frames[2:3]),
            "tiny idle right": animation.Animation(tiny_frames[3:4]),
            "walk down": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[0:8], 70),
                    animation.Animation(torso_frames[0:8], 70),
                    animation.Animation(arm_frames[0:8], 70),
                    animation.Animation(head_frames[0:8], 70),
                )
            ),
            "walk up": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[8:16], 70),
                    animation.Animation(torso_frames[8:16], 70),
                    animation.Animation(arm_frames[8:16], 70),
                    animation.Animation(head_frames[8:16], 70),
                )
            ),
            "walk right": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[16:24], 70),
                    animation.Animation(torso_frames[16:24], 70),
                    animation.Animation(arm_frames[16:24], 70),
                    animation.Animation(head_frames[16:24], 70),
                )
            ),
            "walk left": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[16:24], 70, mirror_x=True),
                    animation.Animation(torso_frames[16:24], 70, mirror_x=True),
                    animation.Animation(arm_frames[16:24], 70, mirror_x=True),
                    animation.Animation(head_frames[16:24], 70, mirror_x=True),
                )
            ),
            "idle down": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[7:8], 70),
                    animation.Animation(torso_frames[7:8], 70),
                    animation.Animation(arm_frames[7:8], 70),
                    animation.Animation(head_frames[7:8], 70),
                )
            ),
            "idle up": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[15:16], 70),
                    animation.Animation(torso_frames[15:16], 70),
                    animation.Animation(arm_frames[15:16], 70),
                    animation.Animation(head_frames[15:16], 70),
                )
            ),
            "idle right": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[23:24], 70),
                    animation.Animation(torso_frames[23:24], 70),
                    animation.Animation(arm_frames[23:24], 70),
                    animation.Animation(head_frames[23:24], 70),
                )
            ),
            "idle left": animation.MultiAnimation(
                (
                    animation.Animation(foot_frames[23:24], 70, mirror_x=True),
                    animation.Animation(torso_frames[23:24], 70, mirror_x=True),
                    animation.Animation(arm_frames[23:24], 70, mirror_x=True),
                    animation.Animation(head_frames[23:24], 70, mirror_x=True),
                )
            ),
        }
        super().__init__(
            pos,
            registry=registry,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, registry.get_group("collision")
            ),
            anim_dict=anim_dict,
            id="player",
            layer=layer,
            start_health=6,
            max_health=12,
            initial_state="idle",
        )
        self.collision_rect = self.rect
        self.speeds = {
            "x": SPEED_WALKING,
            "y": SPEED_WALKING,
        }
        self.current_mana = 6
        self.mana_capacity = 12
        self.items = {
            "sword": 1,
            "cheddar": 3,
            "empty bottle": 2,
            "bug net": 1,
            "key": 5,
        }
        self.save_fields = (
            "current_mana",
            "mana_capacity",
            "current_health",
            "health_capacity",
            "items",
        )
        self.tiny = False
        self.input_locked = False
        self.load_data()
        self.tool = None
        self.carrying = None
        self.facing = "down"
        self.speed = 72

    def heal_mp(self, mp):
        self.current_mana += mp

    def equip(self, name):
        # TODO
        print("equipping", name)
        self.tool = tool.get_tool(self, name)

    def immobilize(self):
        self.input_locked = True

    def unimmobilize(self):
        self.input_locked = False

    def save_data(self):
        for field in self.save_fields:
            globals.engine.state.set(field, getattr(self, field), "player")

    def load_data(self):
        for field in self.save_fields:
            setattr(self, field, globals.engine.state.get(field, "player"))

    def event(self, event):
        if event.type == event_binding.BOUND_EVENT:
            self.command(event.name)

    def command(self, command_name):
        if self.input_locked:
            return
        words = command_name.split(" ")
        if words[0] == "interact":
            self.interact()
        if words[0] == "tool" and self.tool is not None:
            self.tool.use()
        if words[0] == "lift":
            self.pick_up()
        if words[0] == "throw":
            self.throw()
        if words[0] == "start":
            if words[1] == "meandering":
                self.speeds[words[2]] = SPEED_MEANDERING
            if words[1] == "walking":
                self.speeds[words[2]] = SPEED_WALKING
            if words[1] == "running":
                self.speeds[words[2]] = SPEED_RUNNING
            self.speed = max(self.speeds.values())
        if words[0] == "go":
            directions = {
                "up": (self.desired_velocity.x, -self.speed),
                "down": (self.desired_velocity.x, self.speed),
                "left": (-self.speed, self.desired_velocity.y),
                "right": (self.speed, self.desired_velocity.y),
            }
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

    def get_interaction_rect(self):
        interaction_rect = self.rect.copy()
        interaction_rect.height = interaction_rect.width
        interaction_rect.midbottom = self.rect.midbottom
        interaction_rect.center += (
            util.string_direction_to_vec(util.round_string_direction(self.facing)) * 16
        )
        return interaction_rect

    def interact(self):
        for sprite in self.registry.get_group("interactable").sprites():
            if sprite.rect.colliderect(self.get_interaction_rect()):
                sprite.interact()
                print("interacting with sprite", sprite.get_id())
                self.stop()
                break

    def pick_up(self):
        for sprite in self.registry.get_group("throwable").sprites():
            if sprite.rect.colliderect(self.get_interaction_rect()):
                sprite.pick_up()
                break

    def throw(self):
        if self.carrying is not None:
            self.carrying.throw()
        self.carrying = None

    def change_collision_group(self, collision_group):
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)

    def change_layer(self, layer):
        self._layer = layer

    def update_rects(self):
        self.rect = pygame.Rect(self.image.get_rect(center=self.pos))
        self.collision_rect = pygame.Rect(0, 0, 10, 10)
        self.collision_rect.midbottom = self.rect.midbottom

    def get_anim_key(self):
        return ("tiny " * self.tiny) + f"{self.state} {self.facing}"

    def update_state(self, dt):
        super().update_state(dt)

    def update_throwable(self):
        if self.carrying is not None:
            self.carrying.position()

    def update(self, dt):
        self.current_mana = min(self.current_mana + (dt * 0.1), self.mana_capacity)
        super().update(dt)
        self.update_throwable()
