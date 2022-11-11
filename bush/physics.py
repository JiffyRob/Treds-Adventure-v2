"""
physics - underlying physics primitives used by physics components.

You can create your own physics component using a different engine if you would like.
"""
from typing import Sequence, Union

import pygame
import shapely.affinity as affinity
import shapely.geometry as shapes


class Shape:
    """Shape baseclass for Polygons, Circles, Points, and Lines"""

    def __init__(self, shape: Union[shapes.Polygon, shapes.LineString, shapes.Point]):
        self._shape = shape

    def area(self):
        """Area of the shape"""
        return self._shape.area()

    def bounds(self):
        """Bounds of the shape (left, top, right, bottom)"""
        return self._shape.bounds()

    def centroid(self):
        """Centroid of the shape (pygame.Vector2)"""
        return self._shape.centroid()

    def distance(self, other):
        """Return the minimum distance between this shape and the given shape"""
        return self._shape.distance(other._shape)

    def representive_point(self):
        """Return a point guaranteed to be inside this shape"""
        return self._shape.representative_point()

    def move(self, x: float, y: float):
        """Move the shape by the given offset"""
        self._shape = affinity.translate(self._shape, x, y, 0)


class Circle(Shape):
    """A circle"""

    def __init__(self, radius: float, offset: Sequence[float]):
        self._radius = radius
        self._offset = offset
        super().__init__(shapes.Point(offset).buffer(radius))


class Rect(Shape):
    """
    Takes same arguments as pygame.Rect, and has all of the same interfaces, but does NOT inherit from pygame.Rect

    positioning on RigidBodies still uses the rect.center
    """

    def __init__(self, *args, **kwargs):
        self._rect = pygame.Rect(*args, **kwargs)
        Shape.__init__(
            self,
            shapes.Polygon(
                (
                    self._rect.topleft,
                    self._rect.topright,
                    self._rect.bottomright,
                    self._rect.bottomleft,
                )
            ),
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


class Poly(Shape):
    """A polygon"""

    def __init__(
        self,
        outside_points: Sequence[Sequence[float]],
        holes: Sequence[Sequence[float]],
    ):
        super().__init__(shapes.Polygon(outside_points, holes))


class Point(Shape):
    """A Point"""

    def __init__(self, x: float, y: float):
        super().__init__(shapes.Point(x, y))


class LineString(Shape):
    """A string of lines"""

    def __init__(self, coords: Sequence[Sequence[float]]):
        super().__init__(shapes.LineString(coords))


class RigidBody:
    """A Rigid Body with shapes"""

    def __init__(
        self,
        pos: Sequence[float] = (0, 0),
        mass: float = 0,
        restitution: float = 0,
        *shapes: Shape
    ):
        self._shapes = list(shapes)
        self._position = pygame.Vector2(pos)
        self._velocity = pygame.Vector2()
        self._force = pygame.Vector2()
        self._mass = mass
        self._restitution = restitution
        self.layers = 

    def step(self, dt):
        """Step with given dt"""
        self._velocity += (self._force / self._mass) * dt
        self._position += self._velocity * dt


class Space:
    """space for physics simulation"""

    def __init__(self, *bodies):
        self._bodies = []

    def step(self, dt):
        """Step the physics engine"""
        # collision detection?
        # impulse resolution?
        # move objects?

    def add_body(self, *bodies: Sequence[RigidBody]):
        """Add bodies to the Space"""


def get_mass(shape, density):
    """Get mass of a shape from its density"""
    return density * shape.volume
