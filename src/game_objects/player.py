"""
player - class for the player
"""
import pygame

import globals
import inator
from bush import animation, asset_handler, effect, event_binding, physics, util
from game_objects import arg, base

SPEED_MEANDERING = 32
SPEED_WALKING = 96
SPEED_RUNNING = 140

loader = asset_handler.AssetHandler("sprites/player")


class Player(base.MobileGameObject):
    """main player of the game"""

    registry_groups = ()  # do NOT add to any groups on setup, registry will be None
    true_groups = ("main", "player", "attackable", "scriptable")

    def __init__(self):
        tiny_frames = loader.load_spritesheet("tiny.png", (16, 16))
        foot_frames = loader.load_spritesheet("feet-default.png", (16, 32))
        torso_frames = loader.load_spritesheet("torso-default.png", (16, 32))
        arm_frames = loader.load_spritesheet("arms-default.png", (16, 32))
        head_frames = loader.load_spritesheet("head-default.png", (16, 32))
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
            arg.GameObjectArgs(id="player"),
            anim_dict=anim_dict,
            start_health=6,
            max_health=12,
            hit_effect=effect.Flicker(1500),
            immunity=1500,
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

    def reset(self, pos, layer, registry, tiny=False):
        self.throw()
        self.kill()
        self.tiny = tiny
        self.pos = pygame.Vector2(pos)
        self.update_rects()
        self.layer = layer
        self.registry = registry
        for key in self.true_groups:
            self.registry.get_group(key).add(self)
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, self.registry.get_group("collision")
        )

    def heal_mp(self, mp):
        self.current_mana += mp
        self.current_mana = pygame.math.clamp(self.current_mana, 0, self.mana_capacity)

    def get(self, *things):
        """things that begin in '$' are money, things that begin in '~' are health, things that begin in '*' are mana points"""
        for thing in things:
            if thing[0] == "$":
                pass  # TODO: add money
            elif thing[0] == "~":
                self.heal(int(thing[1:]))
            elif thing[0] == "*":
                self.heal_mp(int(thing[1:]))
            else:
                self.items[thing] = self.items.get(thing, 0) + 1

    def lose(self, *things):
        for thing in things:
            if thing[0] == "$":
                pass  # TODO: add money
            elif thing[0] == "~":
                self.hurt(int(thing[1:]))
            elif thing[0] == "*":
                self.heal_mp(-int(thing[1:]))
            elif thing in self.items.keys():
                self.items[thing] -= 1
                if not self.items[thing]:
                    self.items.pop(thing)

    def has(self, thing):
        if thing[0] == "$":
            pass  # TODO: add money
        else:
            return thing in self.items.keys()

    def equip(self, name):
        # TODO
        print("equipping", name)
        self.tool = inator.get_tool(self, name)

    def immobilize(self):
        super().immobilize()
        self.input_locked = True

    def mobilize(self):
        super().mobilize()
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
        if words[0] == "start":
            if words[1] == "meandering":
                self.speeds[words[2]] = SPEED_MEANDERING
            if words[1] == "walking":
                self.speeds[words[2]] = SPEED_WALKING
            if words[1] == "running":
                self.speeds[words[2]] = SPEED_RUNNING
            self.speed = max(self.speeds.values())
            print(words, self.speeds, self.speed)
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
        if self.carrying:
            self.throw()
            return
        for sprite in self.registry.get_group("interactable").sprites():
            if sprite.rect.colliderect(self.get_interaction_rect()):
                sprite.interact()
                print("interacting with sprite", sprite.get_id(), sprite)
                self.stop()
                break

    def pick_up(self, sprite):
        self.carrying = sprite
        return True

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

    def update(self, dt):
        super().update(dt)
        self.current_mana = min(self.current_mana + (dt * 0.1), self.mana_capacity)
        if self.carrying:
            self.carrying.pos = self.pos
            self.carrying.update_rects()

    def on_teleport(self):
        self.throw()

    def limit(self, map_rect):
        if not map_rect.contains(self.rect):
            if globals.engine.stack.get_current().update_map():
                return
        super().limit(map_rect)
