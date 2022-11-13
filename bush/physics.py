"""
physics - underlying physics primitives used by physics components.

You can create your own physics component using a different engine if you would like.
"""
from typing import Sequence, Union

import pygame
import shapely.affinity as affinity
import shapely.geometry as shapes

LAYER1 = 0b1
LAYER2 = 0b10
LAYER3 = 0b100
LAYER4 = 0b1000
LAYER5 = 0b10000
LAYER6 = 0b100000
LAYER7 = 0b1000000
LAYER8 = 0b10000000


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
            surface, (0, 0, 255), pygame.Vector2(origin) + self._rect.topleft
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
        pygame.draw.polygon(surface, (0, 0, 255), points)


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


class RigidBody:
    """A Rigid Body with shapes"""

    def __init__(
        self,
        pos: Sequence[float] = (0, 0),
        mass: float = 0,
        restitution: float = 0,
        layers: Sequence[int] = LAYER1,
        *shapes: Shape,
    ):
        self._shapes = list(shapes)
        self._position = pygame.Vector2(pos)
        self._velocity = pygame.Vector2()
        self._force = pygame.Vector2()
        self._mass = mass
        self._restitution = restitution
        self._layers = 0b00000000
        for layer in layers:
            self._layers |= layer

    def __repr__(self):
        return f"<RigidBody object (pos:{self._position})>"

    def add_to_layer(self, layer: int):
        """Add body to given layer"""
        self._layers |= layer

    def remove_from_layer(self, layer: int):
        """Remove body from given layer (works fine if not in given layer"""
        self._layers &= ~layer

    def in_layer(self, layer: int):
        """Return if body in given layer"""
        return self._layers & layer

    def apply_force(self, force: Sequence[float]):
        """Apply given for to an object"""
        self._force += pygame.Vector2(force)

    def draw(self, surface):
        """Debug draw function"""
        for shape in self._shapes:
            shape.draw(self._position, surface)

    def get_shapes(self, world_space: bool = False):
        """Return a generator of all of this body's shapes, position translated to world space if needed"""
        for shape in self._shapes:
            if world_space:
                shape = affinity.translate(shape, self._position.x, self._position.y)
                yield shape
            yield shape

    @property
    def bounds(self):
        """Return bounds of the object (top, left, bottom, right)"""
        rects = []
        for shape in self.get_shapes(True):
            rect = pygame.Rect(shape.bounds)
            rect.bottomright = shape.bounds[2:]
            rects.append(rect)
        rect = pygame.Rect(rects[0]).unionall(rects[1:])
        return rect.top, rect.left, rect.bottom, rect.right

    def collidebody(self, body):
        """Return if colliding with other body"""
        for shape1 in self.get_shapes(True):
            for shape2 in body.get_shapes(True):
                if shape1.intersects(shape2):
                    return True
        return False


class Space:
    """space for physics simulation"""

    def __init__(self, *bodies: RigidBody):
        self._bodies = bodies

    def step(self, dt):
        """Step the physics engine"""
        # collision detection?
        checked = set()
        resolve = set()
        for body1 in self._bodies:
            for body2 in self._bodies:
                if (
                    (body1 is body2)  # no collision with self
                    or ((body2, body1) in checked)  # pair already checked inverse
                    or not (body2._layers & body1._layers)  # pair not on same layers
                ):
                    continue
                # cheap bounding rect check
                if pygame.Rect(body1.bounds).colliderect(body2.bounds):
                    # expensive shape collision check
                    if body1.collidebody(body2):
                        resolve.add((body1, body2))
                # add to list of checked pairs
                checked.add((body1, body2))
        # impulse resolution?
        if resolve:
            print(resolve)
        # move objects?
        for body in self._bodies:
            body._velocity += (body._force / body._mass) * dt / 1000
            body._position += body._velocity * dt / 1000
            body._force = pygame.Vector2()

    def add_body(self, *bodies: Sequence[RigidBody]):
        """Add bodies to the Space"""
        for body in bodies:
            self._bodies.append(body)

    def remove_body(self, body):
        """Return and remove given body from the space"""
        return self._bodies.remove(body)

    def has_body(self, body):
        """Return if body in the space"""
        return body in self._bodies

    def draw(self, surface: pygame.Surface):
        """Draw the space to the given surface"""
        for body in self._bodies:
            body.draw(surface)


def get_mass(shape, density):
    """Get mass of a shape from its density"""
    return density * shape.volume


def test():
    """A test of the physics engine"""
    body1 = RigidBody((45, 45), 10, 0.5, [LAYER1], Poly.as_circle(6, (0, 0)))
    body2 = RigidBody((45, 100), 10, 0.5, [LAYER1], Poly.as_circle(6, (0, 0)))
    space = Space(body1, body2)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    screen = pygame.display.set_mode((400, 400))
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
        body2.apply_force(vec)
        space.step(dt)
        screen.fill((0, 0, 0))
        space.draw(screen)
        pygame.display.update()
        dt = clock.tick(60)

    pygame.quit()


def q():
    pygame.quit()
