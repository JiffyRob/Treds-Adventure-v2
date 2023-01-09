from bush import timer

try:
    from bush import event_binding
except ImportError:
    print("WARNING: event bindings not found.  InputController object set to None")
    event_binding = None


class Controller:
    def __init__(self):
        self.accepts_events = False

    def generate_commmands(self):
        pass

    def event(self, event):
        pass


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


class EJECSController:
    """EJECS JSON EVENT COORDINATION SYSTEM"""

    def __init__(self, script, command_callbacks):
        self.script = script
        self.current_index = 0
        self.special_names = (":IF", ":VAR")
        self.command_callbacks = {
            "eq": (lambda x, y: x == y, True),
            "neq": (lambda x, y: x != y, True),
            "or": (lambda x, y: x or y, True),
            "and": (lambda x, y: x and y, True),
            ">": (lambda x, y: x > y, True),
            ">=": (lambda x, y: x >= y, True),
            "<": (lambda x, y: x < y, True),
            "<=": (lambda x, y: x <= y, True),
            "max": (max, True),
            "min": (min, True),
            "sum": (sum, True),
            "diff": (lambda x, y: x - y, True),
            "print": (print, True),
            **command_callbacks,
        }
        self.namespace = {
            "true": True,
            "false": False,
        }
        self.current_command = None
        self.wait = False
        super().__init__()

    def return_value(self, value):
        if self.wait:
            if self.wait is not True:
                self.add_to_namespace(self.wait, value)
                self.wait = False
                return True
        return False

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
        if self.wait:
            return None
        command_data = self.script[self.current_index]
        args = ()
        kwargs = {}
        var_name = None
        # command is 'name' 'arg1' 'arg2' ... 'argn' list
        if isinstance(command_data, list):
            next_command, *args = command_data
        # command is {"action": 'name', "kwarg": 'kwarg', [":IF": 'statement', ":VAR": 'var name']} dict
        else:
            next_command = command_data.pop(["action"])
            if_clause = command_data.pop(":IF", "true")
            if not self.evaluate_if(if_clause):
                self.current_index += 1
                return self.generate_commmand()
            var_name = command_data.pop(":VAR", None)
        self.add_to_namespace(
            var_name,
        )
        callback, wait = self.command_callbacks[next_command]
        if wait:
            self.wait = var_name
        else:
            self.wait = False
        return callback
