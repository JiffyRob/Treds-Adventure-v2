"""
physics - simple top down physics + shape primitives
"""
from typing import Sequence, Union

import pygame
import shapely.affinity as affinity
import shapely.geometry as shapes
import shapely.ops as ops

from bush import util

TYPE_STATIC = 1
TYPE_DYNAMIC = 2
TYPE_PUSHABLE = 3
TYPE_FRICTION = 4


def bounding_rect(shape):
    minx, miny, maxx, maxy = shape.bounds
    return pygame.Rect(round(minx), round(miny), round(maxx - minx), round(maxy - miny))


class Shape:
    """Shape baseclass for Polygons, Circles, Points, and Lines.  Adds in-place translation"""

    def geo_move(self, x: float, y: float):
        """Move the shape by the given offset"""
        self.__dict__ = affinity.translate(self._shape, x, y, 0).__dict__

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        """Draw the shape to given surface, offset from given origin"""
        print("WARNING: This shape has no drawing primitives.  Nothing will appear")

    @property
    def bounding_rect(self):
        return bounding_rect(self)


class Rect(Shape, shapes.Polygon):
    """
    Takes width, height, offset values as input parameters.  Other than that, has all of the interfaces of pygame.Rect

    positioning on RigidBodies still uses the rect.center
    """

    def __init__(
        self, width: float = 0, height: float = 0, offset: Sequence[float] = (0, 0)
    ):
        self._rect = pygame.Rect(0, 0, width, height)
        self._rect.center = offset
        super().__init__(
            (
                self._rect.topleft,
                self._rect.topright,
                self._rect.bottomright,
                self._rect.bottomleft,
            )
        )

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        """Draw the rect to a given surface, offset from given origin"""
        pygame.draw.rect(
            surface, (0, 0, 255), pygame.Vector2(origin) + self._rect.topleft, width=1
        )

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return self._rect.__getattribute__(__name)

    def _refresh_rect(self):
        """Used to reset internal rectangle for *_ip methods"""
        self._shape = shapes.Polygon(
            self._rect.topleft,
            self._rect.topright,
            self._rect.bottomright,
            self._rect.bottomleft,
        )

    def move_ip(self, x: float, y: float):
        """Move the rectangle by given x and y values"""
        super().move(x, y)
        return self._rect.move(x, y)

    def inflate_ip(self, x: float, y: float):
        """Grow or shrink the rectangle size, in place"""
        self._rect.inflate_ip(x, y)
        self._refresh_rect()

    def update(self, *args, **kwargs):
        """sets the position and size of the rectangle"""
        self._rect.update(*args, **kwargs)
        self._refresh_rect()

    def clamp_ip(self, other):
        """moves the rectangle inside another, in place"""
        self._rect.clamp_ip(other)
        self._refresh_rect()

    def union_ip(self, other):
        """joins two rectangles into one"""
        self._rect.union_ip(other)
        self._refresh_rect()

    def unionall_ip(self, rect_sequence):
        """the union of many rectangles, in place"""
        self._rect.unionall_ip(rect_sequence)
        self._refresh_rect()

    def normalize(self):
        """correct negative sizes"""
        self._rect.normalize()
        self._refresh_rect()


class Poly(Shape, shapes.Polygon):
    """A polygon"""

    @classmethod
    def as_circle(cls, radius, offset):
        poly = shapes.Point(offset).buffer(radius)
        print("cds: ", list(poly.exterior.coords))
        print("bounds: ", poly.bounds)
        return cls(poly.exterior.coords)

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        points = []
        for point in self.exterior.coords:
            points.append(pygame.Vector2(point) + origin)
        pygame.draw.polygon(surface, (0, 0, 255), points, width=1)


class Point(Shape, shapes.Point):
    """A Point"""

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        pos = pygame.Vector2(origin) + self.coords[0]
        surface.set_at(pos, (0, 0, 255))


class LineString(Shape, shapes.LineString):
    """A string of lines"""

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        points = [pygame.Vector2(i) + origin for i in self.coords]
        pygame.draw.lines(surface, (0, 0, 255), False, points)


class Body(pygame.sprite.Sprite):
    """Rigid body for top down physics"""

    def __init__(
        self,
        pos,
        mass,
        shapes,
        group,
        pushable=False,
        type=TYPE_STATIC,
        friction=3,
        dynamic_collision_hook=lambda body: None,
    ):
        super().__init__(group)
        self.mass = mass
        self.velocity = pygame.Vector2()
        self.shape = Poly(ops.unary_union(shapes))
        bounds = self.shape.bounds
        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.shape.bounding_rect).inflate(1, 1)
        self.rect.center = self.pos
        self.group = group
        self.pushable = pushable
        self.friction = friction
        self.pos = pygame.Vector2(pos)
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.shape.draw((self.rect.width // 2, self.rect.height // 2), self.image)
        # util.debug_view(self.image)
        print(self.rect)
        self.min_speed = 1
        self.dynamic_collision_hook = dynamic_collision_hook
        self.type = type

    @property
    def ws_shape(self):
        return affinity.translate(self.shape, *self.pos)

    def __repr__(self):
        return f"Body ({self.pos}) in ({len(self.groups())}) groups"

    def update(self, dt):
        self.move(self.velocity)
        self.rect.center = self.pos

    def move(self, direc):
        if not direc:
            return
        if self.type == TYPE_STATIC:
            raise TypeError("Cannot move a static body")
        self._try_moving(direc)

    def _try_moving(self, direc):
        xvec = pygame.Vector2(direc.x, 0)
        yvec = pygame.Vector2(0, direc.y)
        # X motion
        if xvec.magnitude_squared():
            xdir = direc.x / abs(direc.x)
            self.pos += xvec
            for body in pygame.sprite.spritecollide(self, self.group, False):
                # collision with self
                if body is self:
                    continue
                # moving objects collide
                if body.type == TYPE_DYNAMIC:
                    self.dynamic_collision_hook(body)
                    continue

                # friction time!
                if body.type == TYPE_FRICTION:
                    friction = body.friction
                    xdist = abs(xvec.x)
                    if abs(xdist) - friction < self.min_speed:
                        friction = xdist - self.min_speed
                    friction *= -xdir
                    self.pos.x += friction
                    continue

                # all that's left is static
                # get intersection of the two shapes
                intersection = self.ws_shape.intersection(body.ws_shape)
                # make sure the polygons collide
                if not intersection.area:
                    continue
                print("XCOLLIDE!")
                # get width of intersection
                bounds = intersection.bounds
                width = bounds[2] - bounds[0]
                # move back
                self.pos.x -= width * xdir
        # Y motion
        if yvec.magnitude_squared():
            ydir = direc.y / abs(direc.y)
            self.pos += yvec
            for body in pygame.sprite.spritecollide(self, self.group, False):
                # collision with self
                if body is self:
                    continue
                # moving objects collide
                if body.type == TYPE_DYNAMIC:
                    self.dynamic_collision_hook(body)
                    continue

                # friction time!
                if body.type == TYPE_FRICTION:
                    friction = body.friction
                    ydist = abs(yvec.y)
                    if abs(ydist) - friction < self.min_speed:
                        friction = ydist - self.min_speed
                    friction *= -ydir
                    self.pos.y += friction
                    continue

                # all that's left is static
                # get intersection of the two shapes
                intersection = self.ws_shape.intersection(body.ws_shape)
                # make sure the polygons collide
                if not intersection.area:
                    continue
                print("YCOLLIDE!")
                # get height of intersection
                bounds = intersection.bounds
                height = bounds[3] - bounds[1]
                print(height, bounds)
                # move back
                self.pos.y -= height * ydir

    def stop(self):
        self.velocity = pygame.Vector2()


class BodyGroup(pygame.sprite.Group):
    def get_bodies(self):
        return self.sprites()


def test():
    screen = pygame.display.set_mode((400, 400))
    body_group = BodyGroup()
    # small arrow key controlled object
    body1 = Body(
        pos=(45, 45),
        mass=10,
        shapes=Poly.as_circle(6, (0, 0)),
        group=body_group,
        type=TYPE_DYNAMIC,
    )
    # identical to body one without control
    body2 = Body((45, 100), 10, Poly.as_circle(6, (0, 0)), body_group)
    # bigger heavier one
    body3 = Body((45, 145), 30, Poly.as_circle(8, (0, 0)), body_group)
    # static rectangle
    body4 = Body((45, 300), 3, Rect(30, 40), body_group)
    # friction rectangle
    body5 = Body((200, 200), 0, Rect(50, 50), body_group, type=TYPE_FRICTION)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        keys = pygame.key.get_pressed()
        vec = pygame.Vector2()
        if keys[pygame.K_UP]:
            vec.y -= 3
        if keys[pygame.K_LEFT]:
            vec.x -= 3
        if keys[pygame.K_DOWN]:
            vec.y += 3
        if keys[pygame.K_RIGHT]:
            vec.x += 3
        body1.move(vec)
        body_group.update(dt)
        body1.stop()
        screen.fill((0, 0, 0))
        body_group.draw(screen)
        pygame.display.update()
        dt = clock.tick(60)


test()
