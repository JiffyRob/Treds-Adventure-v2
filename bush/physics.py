"""
physics - simple top down physics + shape primitives
"""
from typing import Sequence, Union
from bush import util
import pygame
from bush import collision

from bush import util

TYPE_STATIC = 1
TYPE_DYNAMIC = 2
TYPE_PUSHABLE = 3
TYPE_FRICTION = 4


def collide_body(body1, body2):
    if body1 is body2:
        return False
    types = (type(body1), type(body2))
    if DynamicBody not in types:
        return False
    if types == (DynamicBody, StaticBody):
        return collision.collide_rect_mask(body1.rect, body2.mask, body2.rect.topleft)
    if types == (StaticBody, DynamicBody):
        return collision.collide_rect_mask(body2.rect, body1.mask, body1.rect.topleft)
    if types == (DynamicBody, DynamicBody):
        return collision.collide_rect(body1.rect, body2.rect)
    if types == (DynamicBody, TriggerBody):
        return collision.collide_rect_mask(body1.rect, body2.mask, body2.rect.topleft)
    if types == (TriggerBody, DynamicBody):
        return collision.collide_rect_mask(body2.rect, body1.mask, body1.rect.topleft)
    print("collision confused between", types, ". Assuming they don't collide")
    return False


def friction_func(value: float, min_speed: float = 1):
    """Return function that aplies friction of given strength to dynamic bodies"""

    def output(sprite):
        if sprite.velocity:
            print("before", sprite.velocity)
            veloc = -sprite.velocity
            veloc.scale_to_length(
                min(sprite.velocity.length() - min_speed, value)
            )
            sprite.velocity += veloc
            print("after", sprite.velocity)

    return output


class Body(pygame.sprite.Sprite):
    def __repr__(self):
        pos = None
        if hasattr(self, "pos"):
            pos = self.pos
        return f"{type(self)} sprite pos {pos} groups {self.groups()}"


class StaticBody(Body):
    def __init__(self, mask: pygame.Mask, pos: Union[Sequence[float], pygame.Vector2]):
        self.mask = mask
        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.mask.get_rect(center=self.pos))
        self.image = self.mask.to_surface(
            setcolor=(0, 255, 0, 255), unsetcolor=(0, 0, 0, 0)
        ).convert_alpha()
        super().__init__()


class DynamicBody(Body):
    def __init__(self, rect: Sequence[int]):
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill((0, 0, 255))
        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2()
        super().__init__()

    def update(self, dt, velocity=None):
        velocity = velocity or self.velocity
        self.pos += velocity * dt
        self.rect.center = self.pos


class TriggerBody(Body):
    def __init__(
        self,
        mask: pygame.Mask,
        pos: Union[Sequence[float], pygame.Vector2],
        collision_callback=lambda sprite: None,
    ):
        self.mask = mask
        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.mask.get_rect(center=self.pos))
        self.image = self.mask.to_surface(
            setcolor=(0, 255, 0, 255), unsetcolor=(0, 0, 0, 0)
        ).convert_alpha()
        self.collision_callback = collision_callback
        super().__init__()


class BodyGroup(pygame.sprite.AbstractGroup):
    def __init__(self, *sprites):
        self.dynamic = pygame.sprite.Group()
        self.static = pygame.sprite.Group()
        self.trigger = pygame.sprite.Group()
        super().__init__()

    def add(self, *bodies):
        type_dict = {
            StaticBody: self.static,
            DynamicBody: self.dynamic,
            TriggerBody: self.trigger,
        }
        for body in bodies:
            if type(body) not in type_dict:
                print(
                    f"WARNING: bodies of type {type(body)} not allowed.  Not being added."
                )
            type_dict[type(body)].add(body)
            print("adding", body)

    def sprites(self):
        for sprite in self.trigger.sprites():
            yield sprite
        for sprite in self.static.sprites():
            yield sprite
        for sprite in self.dynamic.sprites():
            yield sprite

    def static_sprites(self):
        return self.static.sprites()

    def dynamic_sprites(self):
        return self.dynamic.sprites()

    def trigger_sprites(self):
        return self.trigger.sprites()

    def update(self, dt):
        trigger_collisions = pygame.sprite.groupcollide(
            self.dynamic, self.trigger, False, False, collide_body
        )
        for sprite, colliding in trigger_collisions.items():
            for trigger in colliding:
                trigger.collision_callback(sprite)
        self.dynamic.update(dt)
        static_collisions = pygame.sprite.groupcollide(
            self.dynamic, self.static, False, False, collide_body
        )
        for sprite, colliding in static_collisions.items():
            # TODO
            veloc = -sprite.velocity.normalize()
            for current in colliding:
                while collision.collide_rect_mask(
                    sprite.rect, current.mask, current.rect.topleft
                ):
                    sprite.update(1, veloc)
        dynamic_collisions = pygame.sprite.groupcollide(
            self.dynamic, self.dynamic, False, False, collide_body
        )
        for sprite, colliding in dynamic_collisions.items():
            # TODO
            sprite.pos -= sprite.velocity * dt


def test():
    screen = pygame.display.set_mode((400, 400))
    body_group = BodyGroup()
    # small arrow key controlled object
    body1 = DynamicBody(pygame.Rect(32, 32, 32, 32))
    # identical to body one without control
    body2 = StaticBody(pygame.Mask((16, 16), True), (100, 100))
    # bigger heavier one
    body3 = StaticBody(pygame.Mask((32, 32), True), (50, 100))
    # static rectangle
    body4 = StaticBody(pygame.Mask((32, 32), True), (150, 200))
    # friction rectangle
    body5 = TriggerBody(pygame.Mask((12, 12), True), (300, 90), friction_func(260))

    body_group.add(body1, body2, body3, body4, body5)

    clock = pygame.time.Clock()
    running = True
    dt = 0
    speed = 300
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        keys = pygame.key.get_pressed()
        vec = pygame.Vector2()
        if keys[pygame.K_UP]:
            vec.y -= speed
        if keys[pygame.K_LEFT]:
            vec.x -= speed
        if keys[pygame.K_DOWN]:
            vec.y += speed
        if keys[pygame.K_RIGHT]:
            vec.x += speed
        body1.velocity = vec
        body_group.update(dt / 1000)
        body1.velocity = pygame.Vector2(0)
        screen.fill((0, 0, 0))
        body_group.draw(screen)
        # print(tuple(body_group.sprites()))
        pygame.display.update()
        dt = clock.tick(60)
