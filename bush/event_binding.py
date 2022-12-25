import pygame

from bush import util_load

BOUND_EVENT = pygame.event.custom_type()


def event_to_string(event):
    # all pygame events from pygame 2.1.2 (SDL 2.0.16)
    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        if event.mod != pygame.KMOD_NONE:
            return f"{pygame.event.event_name(event.type)} {event.mod}"
        return f"{pygame.event.event_name(event.type)} {pygame.key.name(event.key)}"
    return pygame.event.event_name(event.type)


class EventHandler:
    def __init__(self, bindings={}):
        self.bindings = bindings

    def load_bindings(self, path):
        self.bindings = util_load.load_json(path)

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
        new_event = pygame.event.Event(
            BOUND_EVENT, id=self.bindings[as_string], original_event=event
        )
        pygame.event.post(new_event)


glob_event = EventHandler()