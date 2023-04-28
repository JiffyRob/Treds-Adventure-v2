import pygame

from bush import util_load

BOUND_EVENT = pygame.event.custom_type()
JOY_AXIS_MAGNITUDE_REACHED = pygame.event.custom_type()

AXIS_MAGNITUDES = {"center": 0.3, "near": 0.7, "far": 3}
INCLUDE_JOY_IDS = False
INCLUDE_AXIS_DIRECTION = True
INCLUDE_AXIS_MAGNITUDE = False
INCLUDE_MOD_KEYS = False
INCLUDE_MOD_KEYS_ON_KEYUP = False
MOD_STRINGS = {
    pygame.KMOD_NONE: "none",
    pygame.KMOD_LSHIFT: "left shift",
    pygame.KMOD_RSHIFT: "right shift",
    pygame.KMOD_SHIFT: "shift",
    pygame.KMOD_LCTRL: "left ctrl",
    pygame.KMOD_RCTRL: "right ctrl",
    pygame.KMOD_CTRL: "ctrl",
    pygame.KMOD_LALT: "left alt",
    pygame.KMOD_RALT: "right alt",
    pygame.KMOD_ALT: "alt",
    pygame.KMOD_LMETA: "left meta",
    pygame.KMOD_RMETA: "right meta",
    pygame.KMOD_META: "meta",
    pygame.KMOD_CAPS: "caplock",
    pygame.KMOD_NUM: "numlock",
    pygame.KMOD_MODE: "AltGr",
}
DISABLED_MOD_KEYS = 0
MOD_ORDER = (
    pygame.KMOD_CTRL,
    pygame.KMOD_ALT,
    pygame.KMOD_SHIFT,
    pygame.KMOD_NUM,
    pygame.KMOD_META,
    pygame.KMOD_CAPS,
    pygame.KMOD_MODE,
    pygame.KMOD_NONE,
)


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


def get_mod_string(mod_num, disabled_mod_keys=None):
    if disabled_mod_keys is None:
        disabled_mod_keys = DISABLED_MOD_KEYS
    mod_num &= ~disabled_mod_keys  # remove disabled keys
    try:
        return MOD_STRINGS[mod_num]
    except KeyError:
        identifiers = []
        for key in MOD_ORDER:
            if mod_num | key:
                identifiers.append(MOD_STRINGS[key])
        return "+".join(identifiers)


def event_to_string(
    event,
    include_mod_keys=None,
    include_mod_keys_on_keyup=None,
    disabled_mod_keys=None,
    include_joy_ids=None,
    include_axis_direction=None,
    include_axis_magnitude=None,
):
    if include_mod_keys is None:
        include_mod_keys = INCLUDE_MOD_KEYS
    if include_mod_keys_on_keyup is None:
        include_mod_keys_on_keyup = INCLUDE_MOD_KEYS_ON_KEYUP
    if disabled_mod_keys is None:
        disabled_mod_keys = DISABLED_MOD_KEYS
    if include_joy_ids is None:
        include_joy_ids = INCLUDE_JOY_IDS
    if include_axis_direction is None:
        include_axis_direction = INCLUDE_AXIS_DIRECTION
    if include_axis_magnitude is None:
        include_axis_magnitude = INCLUDE_AXIS_MAGNITUDE
    if event.type == JOY_AXIS_MAGNITUDE_REACHED:
        identifiers = ["JoyAxisMagnitudeReached"]
    else:
        identifiers = [pygame.event.event_name(event.type)]

    if "Joy" in identifiers[0] and include_joy_ids:
        if hasattr(event, "instance_id"):
            identifiers.append(event.instance_id)
        else:
            identifiers.append(event.device_index)

    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        key_name = pygame.key.name(event.key)
        mod_name = get_mod_string(event.mod, disabled_mod_keys)
        identifiers.append(key_name)
        if (
            include_mod_keys
            and mod_name
            not in {
                key_name,
                MOD_STRINGS[pygame.KMOD_NONE],
            }
            and not (event.type == pygame.KEYUP and include_mod_keys_on_keyup)
        ):
            identifiers.append("mod " + mod_name)

    if event.type in (pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN):
        identifiers.append(event.button)

    if event.type == JOY_AXIS_MAGNITUDE_REACHED:
        identifiers.extend((event.axis, event.magnitude))

    if event.type == pygame.JOYAXISMOTION:
        identifiers.append(event.axis)
        if include_axis_direction:
            identifiers.append(axis_direction(event.value))
        magnitude = axis_magnitude(event.value)
        if include_axis_magnitude:
            identifiers.append(magnitude)
        pygame.event.post(
            pygame.event.Event(
                JOY_AXIS_MAGNITUDE_REACHED,
                instance_id=event.instance_id,
                axis=event.axis,
                magnitude=magnitude,
            )
        )

    return "-".join([str(i) for i in identifiers])


class EventHandler:
    def __init__(
        self,
        bindings=None,
        aux_bindings=None,
        include_mod_keys=None,
        include_mod_keys_on_keyup=None,
        disabled_mod_keys=None,
        include_joy_ids=None,
        include_axis_direction=None,
        include_axis_magnitude=None,
    ):
        self.bindings = bindings or {}
        self.aux_bindings = aux_bindings or {}
        self.disabled = set()
        self.joysticks = dict(enumerate((init_joysticks())))
        self.include_mod_keys = INCLUDE_MOD_KEYS
        self.include_mod_keys_on_keyup = INCLUDE_MOD_KEYS_ON_KEYUP
        self.disabled_mod_keys = DISABLED_MOD_KEYS
        self.set_mod_flags(
            include_mod_keys, include_mod_keys_on_keyup, disabled_mod_keys
        )
        self.include_joy_ids = INCLUDE_JOY_IDS
        self.include_axis_direction = INCLUDE_AXIS_DIRECTION
        self.include_axis_magnitude = INCLUDE_AXIS_MAGNITUDE
        self.set_joy_flags(
            include_joy_ids, include_axis_direction, include_axis_magnitude
        )

    def set_joy_flags(
        self,
        include_joy_ids=None,
        include_axis_direction=None,
        include_axis_magnitude=None,
    ):
        if include_joy_ids is not None:
            self.include_joy_ids = include_joy_ids
        if include_axis_direction is not None:
            self.include_axis_direction = include_axis_direction
        if include_axis_magnitude is not None:
            self.include_axis_magnitude = include_axis_magnitude

    def set_mod_flags(
        self,
        include_mod_keys=None,
        include_mod_keys_on_keyup=None,
        disabled_mod_keys=None,
    ):
        if include_mod_keys is not None:
            self.include_mod_keys = include_mod_keys
        if include_mod_keys_on_keyup is not None:
            self.include_mod_keys_on_keyup = include_mod_keys_on_keyup
        if disabled_mod_keys is not None:
            self.disabled_mod_keys = disabled_mod_keys

    def load_bindings(
        self,
        path,
        keep_old=False,
        load_joy_flags=True,
        load_mod_flags=True,
        aux=False,
    ):
        if keep_old:
            self.update_bindings(util_load.load_json(path), aux=aux)
        else:
            self.set_bindings(util_load.load_json(path), aux=aux)
        bindings = self.bindings
        if aux:
            bindings = self.aux_bindings
        if "joy-flags" in bindings:
            joy_flags = bindings.pop("joy-flags")
            if load_joy_flags:
                self.set_joy_flags(**joy_flags)
        if "mod-flags" in bindings:
            mod_flags = bindings.pop("mod-flags")
            if load_mod_flags:
                self.set_mod_flags(**mod_flags)
        bindings.pop("#", None)  # Remove comment symbol

    def save_bindings(self, path):
        util_load.save_json(self.bindings, path)

    def bind(self, event_string, string_id, aux=False):
        bindings = self.bindings
        if aux:
            bindings = self.aux_bindings
        if event_string not in bindings:
            bindings[event_string] = string_id
        elif isinstance(bindings[event_string], list):
            bindings[event_string].append(string_id)
        else:
            bindings[event_string] = [bindings[event_string], string_id]

    def unbind(self, event_string, aux=False):
        if aux:
            return self.aux_bindings.pop(event_string)
        return self.bindings.pop(event_string)

    def enable_event(self, event_string):
        self.disabled.remove(event_string)

    def disable_event(self, event_string):
        self.disabled.add(event_string)

    def update_bindings(self, bindings, aux=False):
        for event_string, string_id in bindings.items():
            self.bind(event_string, string_id, aux=aux)

    def set_bindings(self, bindings, aux=False):
        self.bindings = {}
        self.update_bindings(bindings, aux=aux)

    def process_event(self, event):
        as_string = event_to_string(
            event,
            include_mod_keys=self.include_mod_keys,
            disabled_mod_keys=self.disabled_mod_keys,
            include_joy_ids=self.include_joy_ids,
            include_axis_direction=self.include_axis_direction,
            include_axis_magnitude=self.include_axis_magnitude,
        )
        for bindings in (self.bindings, self.aux_bindings):
            event_id = bindings.get(as_string, None)
            if event_id is None:
                return
            if not isinstance(event_id, str):
                for event_name in bindings[as_string]:
                    if event_name in self.disabled:
                        continue
                    self.post_event(name=event_name, original_event=event)
            else:
                if event_id in self.disabled:
                    return
                self.post_event(name=bindings[as_string], original_event=event)

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
