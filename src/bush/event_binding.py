import pygame

from bush import util_load

BOUND_EVENT = pygame.event.custom_type()


def event_to_string(event):
    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        return f"{pygame.event.event_name(event.type)}-{pygame.key.name(event.key)}"
    return pygame.event.event_name(event.type)


class EventHandler:
    def __init__(self, bindings={}):
        self.bindings = bindings

    def load_bindings(self, path):
        self.bindings = util_load.load_json(path)
        self.bindings.pop("#", None)  # Remove comment symbol

    def save_bindings(self, path):
        util_load.save_json(self.bindings, path)

    def bind(self, event_string, string_id):
        self.bindings[event_string] = string_id

    def unbind(self, event_string):
        return self.bindings.pop(event_string)

    def update_bindings(self, bindings):
        self.bindings.update(bindings)

    def process_event(self, event):
        as_string = event_to_string(event)
        event_id = self.bindings.get(as_string, None)
        if event_id is None:
            return
        self.post_event(name=self.bindings[as_string], original_event=event)

    def post_event(self, name, **kwargs):
        new_event = pygame.event.Event(BOUND_EVENT, name=name, **kwargs)
        pygame.event.post(new_event)


glob_event = EventHandler()