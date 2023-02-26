import random

import pygame

from bush import event_binding


class JoyCursor(pygame.sprite.Sprite):
    def __init__(
        self,
        surface,
        hotspot,
        joystick_axes=(0, 1),
        joy_axis_tolerance=0.3,
        alternate=None,
        alternate_chance=0,
    ):
        super().__init__()
        self.hotspot = hotspot
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.visible = False
        self.blank_surf = pygame.Surface((0, 0))
        self.image = self.blank_surf
        self.layer = 1000
        self.alternate = alternate or self.surface
        self.alternate_chance = alternate_chance
        self.use_alternate = False
        self.axes = joystick_axes
        self.joy_axis_tolerance = joy_axis_tolerance
        self.speed = 300
        self.velocity = pygame.Vector2()
        self.suspend_motion = False

    def enable(self):
        self.visible = True
        # chance of getting an alternate image as an easter egg
        if random.random() <= self.alternate_chance:
            self.use_alternate = True
        pygame.mouse.set_visible(False)

    def disable(self):
        self.visible = False
        self.use_alternate = False
        pygame.mouse.set_visible(True)

    def hide(self):
        self.visible = False
        self.use_alternate = False
        pygame.mouse.set_visible(False)

    def move_to(self, pos):
        pygame.mouse.set_pos(pos)

    def move_by(self, amount):
        pygame.mouse.set_pos(pygame.mouse.get_pos() + amount)

    def update(self, dt):
        if self.visible:
            if self.use_alternate:
                self.image = self.alternate
            else:
                self.image = self.surface
        else:
            self.image = self.blank_surf
        self.rect.topleft = pygame.mouse.get_pos() - self.hotspot
        if (
            self.velocity.length_squared() > self.joy_axis_tolerance
            and not self.suspend_motion
        ):
            self.move_by(self.velocity * dt)
        self.suspend_motion = False

    def event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > self.joy_axis_tolerance:
                if event.axis == self.axes[0]:
                    self.velocity.x = event.value * self.speed
                if event.axis == self.axes[1]:
                    self.velocity.y = event.value * self.speed
            else:
                if event.axis == self.axes[0]:
                    self.velocity.x = 0
                if event.axis == self.axes[1]:
                    self.velocity.y = 0
        if event.type == pygame.MOUSEMOTION:
            self.suspend_motion = True
        if event.type == event_binding.BOUND_EVENT:
            if event.name == "cursor up":
                self.velocity.y += -1 * self.speed
            if event.name == "cursor down":
                self.velocity.y += 1 * self.speed
            if event.name == "cursor left":
                self.velocity.x += -1 * self.speed
            if event.name == "cursor right":
                self.velocity.x += 1 * self.speed
            if event.name == "cursor stop up":
                self.velocity.y = max(self.velocity.y - 1 * self.speed, 0)
            if event.name == "cursor stop down":
                self.velocity.y = min(self.velocity.y + 1 * self.speed, 0)
            if event.name == "cursor stop left":
                self.velocity.x = max(self.velocity.x - 1 * self.speed, 0)
            if event.name == "cursor stop right":
                self.velocity.x = min(self.velocity.x + 1 * self.speed, 0)
            if event.name == "cursor click left":
                pygame.event.post(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN, pos=pygame.mouse.get_pos(), button=1
                    )
                )
            if event.name == "cursor release left":
                pygame.event.post(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONUP, pos=pygame.mouse.get_pos(), button=1
                    )
                )

    def limit(self, map_rect):
        pass
