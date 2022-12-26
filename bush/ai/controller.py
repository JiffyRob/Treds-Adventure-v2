import queue
import pygame

from bush import util_load, timer
from bush.ai import command

try:
    from bush import event_binding
except ImportError:
    print("WARNING: event bindings not found.")
    event_binding = NotImplemented


class Controller:
    def __init__(self):
        self.accepts_events = False

    def generate_commmands(self):
        pass

    def event(self, event):
        pass


class InputController(Controller):
    def __init__(self, bindings={}):
        super().__init__()
        self.bindings = bindings
        self.accepts_events = True
        self.command_queue = []

    @classmethod
    def from_json(cls, path, callbacks):
        bindings = util_load.load_json(path)
        for key in tuple(bindings.keys()):
            bindings[key] = callbacks[key]
        return cls(bindings)

    def to_json(self, path, string_keys):
        data = {}
        for key, value in self.bindings.items():
            data[key] = string_keys[value]
        util_load.save_json(data, path)

    def event(self, event):
        string_key = event_binding.event_to_string(event)
        callback = self.bindings.get(string_key, lambda x: None)
        self.command_queue.add(command.Command(callback))

    def generate_commands(self):
        commands = self.command_queue
        self.command_queue = []
        return commands


class TimedAI(Controller):
    def __init__(self, delay=1000):
        self.timer = timer.Timer(delay)
        self.timer.finish()
        super().__init__()

    def generate_command(self):
        if self.timer.done():
            self.timer.reset()
            return [self.get_command()]
        return None

    def get_command(self):
        return lambda *args: None
