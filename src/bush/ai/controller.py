import json

from bush import timer, util_load

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
        command = self.bindings.get(string_key, lambda x: None)
        self.command_queue.add(command)

    def generate_commands(self):
        commands = self.command_queue
        self.command_queue = []
        return commands


class TimedController(Controller):
    def __init__(self, delay=1000):
        self.timer = timer.Timer(delay)
        self.timer.finish()
        super().__init__()

    def generate_command(self):
        if self.timer.done():
            self.timer.reset()
            return self.get_command()
        return None

    def get_command(self):
        return lambda *args: None


class EJECSAI:
    "EJECS JSON EVENT COORDINATION SYSTEM"

    def __init__(self, data_string, command_callbacks):
        self.script = json.loads(data_string)
        self.current_index = 0
        self.special_names = (":IF", ":VAR")
        self.command_callbacks = {
            "eq": lambda x, y: x == y,
            "neq": lambda x, y: x != y,
            "or": lambda x, y: x or y,
            "and": lambda x, y: x and y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            "max": max,
            "min": min,
            "sum": sum,
            "diff": lambda x, y: x - y,
            **command_callbacks,
        }
        self.namespace = {
            "true": True,
            "false": False,
        }
        self.current_command = None
        super().__init__()

    def add_to_namespace(self, name, value):
        if value is None:
            return
        self.namespace[name] = value

    def evaluate_if(self, clause):
        if isinstance(clause, list):
            evaluator, *args = clause
            return self.execute(evaluator, *args)
        else:
            return self.namespace[clause]

    def execute(self, action, *args, **kwargs):
        self.command_callbacks[action](*args, **kwargs)

    def generate_commmand(self):
        if self.current_command is not None:
            if not self.current_command.done():
                return
        command_data = self.script[self.current_index]
        args = ()
        kwargs = {}
        var_name = None
        if isinstance(command_data, list):
            next_command, *args = command_data
        else:
            next_command = command_data["action"]
            if_clause = command_data.pop(":IF", "true")
            if not self.evaluate_if(if_clause):
                return
            var_name = command_data.pop(":VAR", None)
        command = self.get_command(next_command, *args, **kwargs)
        return command
