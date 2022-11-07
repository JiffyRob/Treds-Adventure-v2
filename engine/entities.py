"""
Entities.py

Holds basic entity classes
Holds component classes
Holds ComponentRegistry class
"""
import pygame
import pymunk

from . import util


class Entity:
    """
    Entity:

    Has a series of components

    IDs if not given will start at zero and increment 1 for every Entity instantiated
    If using this method of ID generation it is recommended that you call Entity.reset_ids() as needed.
    That will reset the counter back to zero.

    If an ID is given note that the ID counter will not advance.
    """

    _ids: util.IDHandler = util.IDHandler()

    @classmethod
    def reset_ids(cls):
        cls._ids.reset()

    def __init__(
        self,
        id: int | None = None,
        pos: pygame.Vector2 = pygame.Vector2(),
        components: list | tuple | None = None,
    ):
        # set start vars
        self.pos = pygame.Vector2(pos)
        self._id = id or self._ids.next()
        # create components
        components = components or {}
        self._components = {component.get_id(): component for component in components}
        print(self._components)

    def update_all(self, dt):
        """Update all components, in no particaular order"""
        for key in self._components.keys():
            self._components[key].update(dt)

    def get_id(self):
        return self._id

    def get_components(self):
        return {i: j for i, j in self._components.items()}


class ComponentRegistry:
    """
    Component Registry:
     - Keeps track of components of multiple types
     - Has methods for operating on batches of them
    """

    def __init__(self, extra_component_types: tuple = ()):
        self._components = {
            "physics": {},
            "state": {},
            "render": {},
            "input": {},
        }
        for name in extra_component_types:
            self._components[name] = []

    def get_all(self, type: str):
        """Get all components of a specific type"""
        try:
            return list(self._components[type].values())
        except KeyError:
            raise ValueError(
                f"component type given {type} not recognized by this registry.  Allowed are {self._components.keys()}"
            )

    def add_entity(self, entity: Entity, add_new: bool = False):
        """
        Add an entity's components to the registry

        If add_new is true, new types of components will generate new entries in the registry
        Else they will be ignored
        """
        for _, component in entity.get_components().items():
            type = component.get_type()
            if type in self._components:
                self._components[type][component.get_id()] = component
            elif add_new:
                self._components[type] = {component.get_id(): component}
        print(self._components)

    def update(self, dt: float, type: str | None = None):
        """
        Update components of a specific type
        params:
         - dt: float = delta time
         - type: str | None = component type to update.  None updates everything (NOT recommended)
        """
        try:
            components = self._components[type]
        except KeyError:
            if type == None:
                for key, component_dict in self._components.items():
                    for component in component_dict.values():
                        component.update(dt)
                return
            raise ValueError(
                f"component type given {type} not recognized by this registry.  Allowed are {self._components.keys()}"
            )
        for c in components.values():
            c.update(dt)

    def render(self, surf: pygame.Surface):
        """Render all render components to give surface"""
        for component in self.get_all("render"):
            component.render(surf)


class Component:
    """
    Base class of all Entity Components
    A Component adds functionality to an Entity
    It has its own type and id, as well as the id of its entities

    ids not auto assigned as in Entity.  Must be passed in manually
    """

    def __init__(self, entity: Entity, id: int):
        self._id = id
        self._entities = [entity]
        self._type = "undef"

    def update(self, dt: float):
        """Update this component"""
        pass

    def get_entities(self):
        return [i for i in self._entities]

    def get_type(self):
        return self._type

    def get_id(self):
        return self._id

    def __repr__(self):
        return f"{self.get_type()} component"


class NullComponent(Component):
    """
    A Do Nothing Component
    """

    def __init__(self, entity: Entity, id: int, type: str = "NULL"):
        self._entities = []
        self._id = None
        self_type = type

    def __getattr__(self, attr):
        return util.CallableNone()


class GeometryRender(Component):
    """
    Rendering Component - renders a shape.

    Takes a dict showing what type of shape to render (Or None, will draw nothing):
    {
        "shape": "circle" for pygame.draw.circle | "rect" for pygame.draw.rect | "polygon" for pygame.draw.polygon
        "params": params to give to respective draw function
        "callable params": params that will be called and the return values given to respective draw function
    }
    """

    def __init__(self, entity: Entity, id: int, params: dict | None = None):
        super().__init__(entity, id)
        self._params = params
        self._callback_dict = {
            "circle": pygame.draw.circle,
            "rect": pygame.draw.rect,
            "polygon": pygame.draw.polygon,
        }
        self._type = "render"

    def change_params(self, **changes):
        """Change params of the geometry draw"""
        if self._params == None:
            self._params = changes
        else:
            self._params = {**self._params, **changes}

    def render(self, surf):
        print("render")
        shape = self._params["shape"]
        params = self._params["params"]
        callback = self._callback_dict[shape]
        for entity in self._entities:
            if shape == "circle":
                callback(**params, center=entity.pos, surface=surf)
            if shape == "rect":
                callback(**params, rect=entity.get_rect(), surface=surf)
            if shape == "polygon":
                callback(**params, points=entity.get_polypoints(), surface=surf)


class ImageRender(Component):
    """Component to render a static image"""

    def __init__(self, entity: Entity, id: int, image: pygame.Surface):
        super().__init__(entity, id)
        self.image = image
        self._type = "render"

    def render(self, surf):
        """Render the image at all entity positions"""
        for entity in self._entities:
            surf.blit(self.image, entity.pos)


class AnimRender(Component):
    """Component to render a single animation"""

    ...


class StateRender(Component):
    """Component to render different animations based on state"""

    ...


class RigidBodyComponent(Component):
    """
    Pymunk rigid body to do physics with

    rb_params: dict = **kwargs to give to pymunk.Body of the component
    see https://www.pymunk.org/en/latest/pymunk.html#pymunk.Body for details

    shapes: tuple = tuple of pymunk shape dicts:
        type: "circle" | "poly" = what type of shape it is
        params: params to pass to corresponding constructor

    see:
        https://www.pymunk.org/en/latest/pymunk.html#pymunk.Poly (poly)
        https://www.pymunk.org/en/latest/pymunk.html#pymunk.Circle (circle)
    """

    def __init__(
        self,
        entity: Entity,
        id: int,
        rb_params: dict,
        shapes: tuple[dict | pymunk.Shape] | None = None,
    ):
        super().__init__(entity, id)
        self._body = pymunk.Body(**rb_params)
        shapes = shapes or ()
        for shape in shapes:
            # try to get type of shape
            try:
                type = shape["type"]
            except:
                raise ValueError("Invalid shape dict {shape}")
            del shape["type"]
            # make shape
            if type == "circle":
                shape = pymunk.Circle(body=self._body, **shape)
            elif type == "poly":
                shape = pymunk.Poly(body=self._body, **shape)
            else:
                raise ValueError(
                    f"Shape type {type} not recognized.  Recognized are 'circle', 'poly'"
                )

    def update(self, dt):
        """update the physics on this component"""
        pass  # for now


class StateComponent(Component):
    """Component to deal with finite state machines"""

    ...


class StateStackComponent(Component):
    """Component to deal with a state stack"""

    ...


class HealthComponent(Component):
    """Component to deal with hp and death"""

    ...


class BasicKeyInput(Component):
    """
    Component to deal with basic input

    Takes a dict of pygame.KEY constants to callbacks.  (Default None -> {})
    Every frame when those keys are down, the corresponding callbacks will be called

    Needs updated every frame

    if dt is true, dt is passed to callbacks as well
    """

    def __init__(
        self, entity: Entity, id: int, input_callbacks: dict | None = {}, dt=False
    ):
        super().__init__(entity, id)
        self._input_callbacks = input_callbacks
        self._type = "input"

    def update(self, dt):
        """Check for downed keys and act on them"""
        keys = pygame.key.get_pressed()
        for key, callback in self._input_callbacks.items():
            if keys[key]:
                if dt:
                    callback(dt)
                else:
                    callback()

    def take_event(self, event):
        return False
