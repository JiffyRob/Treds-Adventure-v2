"""
physics - simple top down physics + shape primitives
"""
from typing import Sequence, Union

import pygame
import shapely.affinity as affinity
import shapely.geometry as shapes
import shapely.ops as ops


class Shape:
    """Shape baseclass for Polygons, Circles, Points, and Lines.  Adds in-place translation"""

    def geo_move(self, x: float, y: float):
        """Move the shape by the given offset"""
        self.__dict__ = affinity.translate(self._shape, x, y, 0).__dict__

    def draw(self, origin: Sequence[float], surface: pygame.Surface):
        """Draw the shape to given surface, offset from given origin"""
        print("WARNING: This shape has no drawing primitives.  Nothing will appear")


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

    def __init__(self, pos, mass, shapes, group, pushable=False, min_speed=1):
        super().__init__(group)
        self.mass = mass
        self.velocity = pygame.Vector2()
        self.shape = Poly(ops.unary_union(shapes))
        bounds = self.shape.bounds
        self.rect = pygame.Rect(*self.pos, 0, 0)
        self.rect.bottomright = bounds[2:]
        self.group = group
        self.pushable = pushable
        self.friction = 0
        self.pos = pygame.Vector2(pos)
        self.image = pygame.Surface(self.rect.size)
        self.shape.draw((0, 0), self.image)
        self.min_speed = 1

    def update(self, dt):
        if self.velocity:
            friction = -self.velocity.copy()
            friction.scale_to_length(min(self.friction, 1))
            self.pos += self.velocity + friction * dt
        self.rect.topleft = self.pos

    def move(self, direc):
        self.velocity += direc

    def stop(self):
        self.velocity = pygame.Vector2()

    def handle_collisions(self):
        for body in self.group.get_bodies():
            # don't move away from pushables (yet)
            if body.pushable:
                continue
            normal, depth = self.collision_data(body)
            if normal is None:
                continue
            if normal.x:
                self.velocity.x = 0
            if normal.y:
                self.velocity.y = 0
            self.pos += normal * depth

    def collision_data(self, other):
        if self.rect.colliderect(other.rect):
            intersection = self.shape.intersection(other.shape)
            if intersection.area:
                # get direction of "bounce"
                if self.velocity:
                    normal_direc = -self.velocity
                else:
                    normal_direc = (other.pos - self.pos).normalize()
                # rotate collision polygon so that bounce direction becomes axis aligned
                turn_degrees = normal_direc.angle_to(pygame.Vector2(-1, 0))
                collision_polygon = affinity.rotate(collision_polygon, turn_degrees)
                # get aabb of shape
                bounds = collision_polygon.bounds
                # get width of aabb
                width = bounds[3] - bounds[1]
                # create a vector with shape and direction
                print(width * normal_direc)
                return normal_direc, width
        return None, 0


class BodyGroup(pygame.sprite.Group):
    def get_bodies(self):
        return self.sprites()


def test():
    screen = pygame.display.set_mode((400, 400))
    body_group = BodyGroup()
    # small arrow key controlled object
    body1 = Body((45, 45), 10, Poly.as_circle(6, (0, 0)), body_group)
    # identical to body one without control
    body2 = Body((45, 100), 10, Poly.as_circle(6, (0, 0)), body_group)
    # bigger heavier one
    body3 = Body((45, 145), 30, Poly.as_circle(8, (0, 0)), body_group)
    # static rectangle
    body4 = Body((45, 300), 3, Rect(30, 40), body_group)
    # friction rectangle
    clock = pygame.time.Clock()
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        vec = pygame.Vector2()
        if keys[pygame.K_UP]:
            vec.y -= 100
        if keys[pygame.K_LEFT]:
            vec.x -= 100
        if keys[pygame.K_DOWN]:
            vec.y += 100
        if keys[pygame.K_RIGHT]:
            vec.x += 100
        body1.move(vec * dt / 1000)
        body_group.update(dt)
        screen.fill((0, 0, 0))
        body_group.draw(screen)
        pygame.display.update()
        dt = clock.tick(60)

    pygame.quit()
