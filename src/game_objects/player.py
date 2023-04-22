"""
player - class for the player
"""
import pygame

SPEED_MEANDERING = 32
SPEED_WALKING = 96
SPEED_RUNNING = 128

from bush import animation, asset_handler, event_binding, physics, util
from game_objects import base

loader = asset_handler.AssetHandler("resources/sprites/player")


class Player(base.DynamicGameObject):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(self, pos, layer, map_env, engine, interactable_group, **__):
        tiny_frames = loader.load(
            "tiny.png", loader=asset_handler.load_spritesheet, frame_size=(16, 16)
        )
        foot_frames = loader.load(
            "feet-default.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 32),
        )
        torso_frames = loader.load(
            "torso-default.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 32),
        )
        arm_frames = loader.load(
            "arms-default.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 32),
        )
        head_frames = loader.load(
            "head-default.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 32),
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
            pygame.Surface((16, 16)),
            engine,
            map_env=map_env,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, pygame.sprite.Group()
            ),
            speed=72,
            anim_dict=anim_dict,
            id="player",
            layer=layer,
            start_health=6,
            max_health=12,
        )
        self.collision_rect = self.rect
        self.engine = engine
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
        self.save_state = self.engine.state
        self.save_fields = (
            "current_mana",
            "mana_capacity",
            "current_health",
            "health_capacity",
            "items",
        )
        self.tiny = False
        self.interactable_group = interactable_group
        self.interactor = None
        self.input_locked = False
        self.load_data()

    def heal_mp(self, mp):
        self.current_mana += mp

    def equip(self, name):
        # TODO
        print("equipping", name, "but not really, coz that's not implemented yet!")

    def save_data(self):
        for field in self.save_fields:
            self.save_state.set(field, getattr(self, field), "player")

    def load_data(self):
        for field in self.save_fields:
            setattr(self, field, self.save_state.get(field, "player"))

    def event(self, event):
        if event.type == event_binding.BOUND_EVENT and not self.input_locked:
            self.command(event.name)

    def command(self, command_name):
        words = command_name.split(" ")
        if words[0] == "interact":
            self.interact()
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
        for sprite in self.interactable_group.sprites():
            if sprite.rect.colliderect(self.get_interaction_rect()):
                sprite.interact()
                print("interacting with sprite", sprite.get_id())
                self.interactor = sprite
                self.stop(True)
                break

    def change_collision_group(self, collision_group):
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, collision_group)

    def change_layer(self, layer):
        self._layer = layer

    def update_rects(self):
        self.rect = self.image.get_rect(center=self.pos)
        self.collision_rect = pygame.Rect(0, 0, 10, 10)
        self.collision_rect.midbottom = self.rect.midbottom
        self.mask = pygame.Mask(self.rect.size, False)
        self.mask.draw(
            pygame.Mask(self.collision_rect.size, True),
            self.collision_rect.topleft - pygame.Vector2(self.rect.topleft),
        )

    def update_state(self):
        super().update_state()
        if self.tiny:
            self.state = "tiny " + self.state
        if self.interactor is not None:
            if self.interactor.interacting:
                self.input_locked = True
            else:
                self.input_locked = False
                self.interactor = None

    def update(self, dt):
        self.current_mana = min(self.current_mana + (dt * 0.1), self.mana_capacity)
        super().update(dt)
