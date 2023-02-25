import pygame

from bush import util_load

BOUND_EVENT = pygame.event.custom_type()
AXIS_MAGNITUDES = {"center": 0.2, "near": 0.6, "far": 3}
INCLUDE_JOY_IDS = False
INCLUDE_AXIS_DIRECTION = True
INCLUDE_AXIS_MAGNITUDE = False


def axis_direction(num):
    tolerance = AXIS_MAGNITUDES["center"]
    if abs(num) < tolerance:
        return "center"
    if num < tolerance:
        return "back"
    if num > tolerance:
        return "forward"


def axis_magnitude(num):
    num = abs(num)
    for key, value in AXIS_MAGNITUDES.items():
        if num < value:
            return key


def event_to_string(
    event,
    include_joy_ids=None,
    include_axis_direction=None,
    include_axis_magnitude=None,
):
    include_joy_ids = include_joy_ids or INCLUDE_JOY_IDS
    include_axis_direction = include_axis_direction or INCLUDE_AXIS_DIRECTION
    include_axis_magnitude = include_axis_magnitude or INCLUDE_AXIS_MAGNITUDE
    identifiers = [pygame.event.event_name(event.type)]
    if "Joy" in identifiers[0] and include_joy_ids:
        if hasattr(event, "instance_id"):
            identifiers.append(event.instance_id)
        else:
            identifiers.append(event.device_index)
    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        identifiers.append(pygame.key.name(event.key))
    if event.type in (pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN):
        identifiers.append(event.button)
    if event.type == pygame.JOYAXISMOTION:
        identifiers.append(event.axis)
        if include_axis_direction:
            identifiers.append(axis_direction(event.value))
        if include_axis_magnitude:
            identifiers.append(axis_magnitude(event.value))
    return "-".join([str(i) for i in identifiers])


class EventHandler:
    def __init__(
        self,
        bindings=None,
        include_joy_ids=None,
        include_axis_direction=None,
        include_axis_magnitude=None,
    ):
        self.bindings = bindings or {}
        self.disabled = set()
        self.joysticks = dict(enumerate((init_joysticks())))
        self.include_joy_ids = None
        self.include_axis_direction = None
        self.include_axis_magnitude = None
        self.set_joy_flags(
            include_joy_ids, include_axis_direction, include_axis_magnitude
        )

    def set_joy_flags(
        self,
        include_joy_ids=None,
        include_axis_direction=None,
        include_axis_magnitude=None,
    ):
        self.include_joy_ids = include_joy_ids or INCLUDE_JOY_IDS
        self.include_axis_direction = include_axis_direction or INCLUDE_AXIS_DIRECTION
        self.include_axis_magnitude = include_axis_magnitude or INCLUDE_AXIS_MAGNITUDE

    def load_bindings(self, path, keep_old=False, load_joy_flags=True):
        if keep_old:
            self.update_bindings(util_load.load_json(path))
        else:
            self.bindings = util_load.load_json(path)
        if "joy-flags" in self.bindings:
            joy_flags = self.bindings.pop("joy-flags")
            if load_joy_flags:
                self.set_joy_flags(**joy_flags)
        self.bindings.pop("#", None)  # Remove comment symbol

    def save_bindings(self, path):
        util_load.save_json(self.bindings, path)

    def bind(self, event_string, string_id):
        if event_string not in self.bindings:
            self.bindings[event_string] = string_id
        elif isinstance(self.bindings[event_string], list):
            self.bindings[event_string].append(string_id)
        else:
            self.bindings[event_string] = [self.bindings[event_string], string_id]

    def unbind(self, event_string):
        return self.bindings.pop(event_string)

    def enable_event(self, event_string):
        self.disabled.remove(event_string)

    def disable_event(self, event_string):
        self.disabled.add(event_string)

    def update_bindings(self, bindings):
        for event_string, string_id in bindings.items():
            self.bind(event_string, string_id)

    def process_event(self, event):
        as_string = event_to_string(
            event,
            include_joy_ids=self.include_joy_ids,
            include_axis_direction=self.include_axis_direction,
            include_axis_magnitude=self.include_axis_magnitude,
        )
        print(as_string)
        event_id = self.bindings.get(as_string, None)
        if event_id is None:
            return
        if not isinstance(event_id, str):
            for event_name in self.bindings[as_string]:
                if event_name in self.disabled:
                    continue
                self.post_event(name=event_name, original_event=event)
        else:
            if event_id in self.disabled:
                return
            self.post_event(name=self.bindings[as_string], original_event=event)

    def post_event(self, name, **kwargs):
        new_event = pygame.event.Event(BOUND_EVENT, name=name, **kwargs)
        pygame.event.post(new_event)

    def add_joystick(self, id):
        if id not in self.joysticks:
            self.joysticks[id] = pygame.joystick.Joystick(id)
            self.joysticks[id].init()

    def remove_joystick(self, id):
        self.joysticks[id].quit()


def init_joysticks():
    pygame.joystick.init()
    print(pygame.joystick.get_count())
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        yield joy


def interactive_id_printer():
    pygame.init()
    pygame.font.init()
    print(pygame.joystick.get_init())
    joys = list(init_joysticks())
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    surface = font.render(
        "Events will be printed to console as strings", True, "black", "white"
    )
    screen = pygame.display.set_mode(surface.get_size())
    screen.blit(surface, (0, 0))
    running = True
    while running:
        for event in pygame.event.get():
            print(event_to_string(event))
            if event.type == pygame.QUIT:
                running = False
        clock.tick(60)
        pygame.display.update()
    pygame.quit()


glob_event = EventHandler()
