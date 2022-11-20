"""
physics - underlying physics primitives used by physics components.

You can create your own physics component using a different engine if you would like.
"""
from typing import Sequence, Union

import pygame
import shapely.affinity as affinity
import shapely.geometry as shapes
import shapely.ops as ops

# layer constants
LAYERF = 0b1
LAYER1 = 0b10
LAYER2 = 0b100
LAYER3 = 0b1000
LAYER4 = 0b10000
LAYER5 = 0b100000
LAYER6 = 0b1000000
LAYER7 = 0b10000000


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


class RigidBody:
    """A Rigid Body with shapes"""

    # init methods
    def __init__(
        self,
        pos: Sequence[float] = (0, 0),
        mass: float = 0,
        restitution: float = 0,
        layers: Sequence[int] = (LAYER1, LAYERF),
        friction: Sequence[float] = (0.25, 0.25),
        shapes: Sequence[Poly | Rect] = (),
    ):
        self._shape = ops.unary_union(shapes)
        self._shape = Poly(self._shape.exterior.coords)
        self._position = pygame.Vector2(pos)
        self._velocity = pygame.Vector2()
        self._force = pygame.Vector2()
        self._restitution = restitution
        self._static_friction, self._dynamic_friction = friction
        self._kinematic_velocty = pygame.Vector2()
        if mass > 0:
            self._mass = mass
            self._inverse_mass = 1 / mass
        else:
            self._mass = self._inverse_mass = 0
        self._layers = 0b00000000
        for layer in layers:
            self._layers |= layer

    @classmethod
    def as_dynamic(
        cls,
        pos: Sequence[float] = (0, 0),
        mass: float = 0,
        restitution: float = 0,
        layers: Sequence[int] = (LAYER1, LAYERF),
        friction: Sequence[float] = (0.25, 0.25),
        shapes: Sequence[Poly | Rect] = (),
    ):
        assert tuple(layers) != LAYERF
        return cls(pos, mass, restitution, layers, friction, shapes)

    @classmethod
    def as_static(
        cls,
        pos: Sequence[float] = (0, 0),
        restitution: float = 0,
        layers: Sequence[int] = (LAYER1, LAYERF),
        friction: Sequence[float] = (0.25, 0.25),
        shapes: Sequence[Poly | Rect] = (),
    ):
        assert tuple(layers) != LAYERF
        return cls(pos, 0, restitution, layers, friction, shapes)

    @classmethod
    def as_kinematic(
        cls,
        pos: Sequence[float] = (0, 0),
        restitution: float = 0,
        layers: Sequence[int] = (LAYER1, LAYERF),
        friction: Sequence[float] = (0.25, 0.25),
        shapes: Sequence[Poly | Rect] = (),
    ):
        assert tuple(layers) != LAYERF
        return cls(pos, 0, restitution, layers, friction, shapes)

    @classmethod
    def as_friction_space(
        cls,
        pos: Sequence[float] = (0, 0),
        friction: Sequence[float] = (0.25, 0.25),
        shapes: Sequence[Poly | Rect] = (),
    ):
        return cls(pos, 0, 0, (LAYERF,), friction, shapes)

    # print
    def __repr__(self):
        return f"<RigidBody object (pos:{self._position})>"

    # layer methods
    def add_to_layer(self, layer: int):
        """Add body to given layer"""
        self._layers |= layer

    def remove_from_layer(self, layer: int):
        """Remove body from given layer (works fine if not in given layer"""
        self._layers &= ~layer

    def in_layer(self, layer: int):
        """Return if body in given layer"""
        return self._layers & layer

    # motion methods
    def apply_force(self, force: Sequence[float]):
        """Apply given for to an object"""
        self._force += pygame.Vector2(force)

    def move(self, offset):
        """Move the object"""
        assert self._layers != LAYERF and self._mass == 0
        self._kinematic_velocty += offset

    # drawing method
    def draw(self, surface):
        """Debug draw function"""
        self._shape.draw(self._position, surface)

    # geometry
    def get_shape(self, world_space: bool = True):
        """Return a copy of this body's shape"""
        if world_space:
            return affinity.translate(self._shape, *self._position)
        return self._shape.copy()

    @property
    def bounds(self):
        """Return bounds of the object (top, left, bottom, right)"""
        return self._shape.bounds

    def collidebody(self, body):
        """Return if colliding with other body"""
        return self.get_shape().intersects(body.get_shape())

    def get_normal(self, other):
        """Return collision normal with other body"""
        # get polygon representing collision
        collision_polygon = self.get_shape().intersection(other.get_shape())
        # get direction of "bounce"
        normal_direc = pygame.Vector2(other._position - self._position).normalize()
        # rotate collision polygon so that bounce direction becomes axis aligned
        turn_degrees = normal_direc.angle_to(pygame.Vector2(-1, 0))
        collision_polygon = affinity.rotate(collision_polygon, turn_degrees)
        # get aabb of shape
        bounds = collision_polygon.bounds
        print(bounds)
        if not bounds:
            return pygame.Vector2(), 0
        # get width of aabb
        width = bounds[3] - bounds[1]
        # create a vector with shape and direction
        print(width * normal_direc)
        return normal_direc, width


class Space:
    """
    space for physics simulation

    warp_values (int, int) = size of simulation space.  If an object's position exits this it warps around to the beginning
    """

    def __init__(
        self,
        warp_values: Union[Sequence[int], None] = None,
        friction: float = 0.1,
        *bodies: RigidBody,
    ):
        self._bodies = bodies
        self.warp = warp_values
        self.friction = friction

    def step(self, dt):
        """Step the physics engine"""
        # collision detection?
        checked = set()
        resolve = set()
        friction = set()
        for body1 in self._bodies:
            for body2 in self._bodies:
                if (body1 is body2) or (  # no collision with self
                    ((body2, body1) in checked)  # pair already checked inverse
                    or (not body1._layers & body2._layers)  # not on same layer
                    or (  # both friction bodies
                        body1._layers == LAYERF == body2._layers
                    )
                ):
                    continue

                # cheap bounding rect check
                if pygame.Rect(body1.bounds).colliderect(body2.bounds):
                    # expensive shape collision check
                    if body1.collidebody(body2):
                        if body1._layers == LAYERF:
                            friction.add((body1, body2))
                            continue
                        if body2._layers == LAYERF:
                            friction.add((body2, body1))
                            continue
                        resolve.add((body1, body2))
                # add to list of checked pairs
                checked.add((body1, body2))

        # fake friction
        for friction_body, receiving_body in friction:
            print("fric")
            if receiving_body._velocity.magnitude_squared():
                friction = friction_body._dynamic_friction
                friction_vector = -receiving_body._velocity
                friction_vector.scale_to_length(
                    min(friction, receiving_body._velocity.magnitude())
                )
                receiving_body._velocity += friction_vector
                friction_vector.scale_to_length(
                    min(friction, receiving_body._kinematic.magnitude())
                )
                receiving_body._kinematic_velocity += friction_vector

        # motion
        for body in self._bodies:
            body._velocity += (body._force * body._inverse_mass) * dt / 1000
            body._position += body._velocity * dt / 1000
            body._position += body._kinematic_velocty
            body._kinematic_velocty.xy = (0, 0)
            body._force = pygame.Vector2()

        # fake impulse resolution
        for body1, body2 in resolve:
            collision_normal, collision_depth = body1.get_normal(body2)
            mass_sum = body1._inverse_mass + body2._inverse_mass
            body1_motion = (
                collision_normal * collision_depth * body1._inverse_mass / mass_sum
            )
            body2_motion = (
                collision_normal * collision_depth * body2._inverse_mass / mass_sum
            )
            body1._velocity -= body1_motion
            body2._velocity += body2_motion

        # warping
        if self.warp:
            for body in self._bodies:
                x_off = body._position.x - self.warp[0]
                if x_off > 0:
                    body._position.x = x_off
                if body._position.x < 0:
                    body._position.x = -x_off
                y_off = body._position.y - self.warp[1]
                if y_off > 0:
                    body._position.y = y_off
                if body._position.y < 0:
                    body._position.y = -y_off

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
    # small arrow key controlled object
    body1 = RigidBody.as_kinematic(
        (45, 45), restitution=1.5, shapes=Poly.as_circle(6, (0, 0))
    )
    # identical to body one without control
    body2 = RigidBody.as_dynamic((45, 100), 10, 1.5, shapes=Poly.as_circle(6, (0, 0)))
    # bigger heavier one
    body3 = RigidBody.as_dynamic((45, 145), 30, 3, shapes=Poly.as_circle(8, (0, 0)))
    # static rectangle
    body4 = RigidBody.as_static((45, 300), 3, [LAYER1], (1.25, 1.25), Rect(30, 40))
    # friction rectangle
    fric1 = RigidBody.as_friction_space((300, 300), (0.25, 0.9), Rect(30, 30))
    space = Space((400, 400), 0.01, body1, body2, body3, body4, fric1)
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
        body1.move(vec * dt / 1000)
        space.step(dt)
        screen.fill((0, 0, 0))
        space.draw(screen)
        pygame.display.update()
        dt = clock.tick(60)

    pygame.quit()


def q():
    pygame.quit()


if __name__ == "__main__":
    test()
