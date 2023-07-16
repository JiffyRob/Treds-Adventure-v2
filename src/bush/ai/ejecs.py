import pygame

try:
    from bush import event_binding
except ImportError:
    print("WARNING: event bindings not found.  InputController object set to None")
    event_binding = None


PROCESS_UNFINISHED = ":PROCESS_UNFINISHED"
IF_UNMET = ":IF_UNMET"


def ejecs_command(function):
    """Decorator that takes a callback and turns it into a command (yields value instead of returns it)"""

    def command_callback(*args, **kwargs):
        yield function(*args, **kwargs)

    return command_callback


class EJECSController:
    """EJECS JSON EVENT COORDINATION SYSTEM"""

    def __init__(self, script, extra_commands):
        self.script = []
        for line in script:
            if isinstance(line, (list, tuple)):
                if line[0] != "#":
                    self.script.append(line)
            else:
                self.script.append(line)
        self.current_index = -1
        self.current_process = iter((0,))
        self.return_name = None
        self.special_names = (":IF", ":VAR")
        self.command_callbacks = None
        self.reset_commands(extra_commands)
        self.namespace = {
            "true": True,
            "false": False,
        }
        super().__init__()

    def reset_commands(self, extra_commands):
        def delay(milliseconds):
            start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start < milliseconds:
                yield PROCESS_UNFINISHED
            yield True

        self.command_callbacks = {
            "eq": ejecs_command(lambda x, y: x == y),
            "neq": ejecs_command(lambda x, y: x != y),
            "or": ejecs_command(lambda x, y: x or y),
            "and": ejecs_command(lambda x, y: x and y),
            ">": ejecs_command(lambda x, y: x > y),
            ">=": ejecs_command(lambda x, y: x >= y),
            "<": ejecs_command(lambda x, y: x < y),
            "<=": ejecs_command(lambda x, y: x <= y),
            "max": ejecs_command(max),
            "min": ejecs_command(min),
            "sum": ejecs_command(sum),
            "diff": ejecs_command(lambda x, y: x - y),
            "print": ejecs_command(
                lambda value, *args, **kwargs: print(
                    "EJECS Script:", value, *args, **kwargs
                )
            ),
            "wait": delay,
            **extra_commands,
        }

    def evaluate(self, exp):
        if isinstance(exp, (list, tuple, dict)):
            return self.execute(exp, True)
        if exp in self.namespace:
            return self.namespace[exp]
        for creator in (int, float, str):
            try:
                return creator(exp)
            except (TypeError, ValueError):
                continue
        raise ValueError(
            f"Given expression {exp} is not an action, variable, integer, float, or string"
        )

    def execute(self, command, return_value=False):
        if isinstance(command, (list, tuple)):
            name, *args = command
            if return_value:
                return next(self.command_callbacks[name](*args))
            self.current_process = self.command_callbacks[name](*args)
        if isinstance(command, dict):
            name = command.pop("action")
            args = command.pop("args", ())
            self.return_name = command.pop(":VAR", None)
            if not self.evaluate(command.pop(":IF", "true")):
                return IF_UNMET
            if return_value:
                return next(self.command_callbacks[name](*args, **command))
            self.current_process = self.command_callbacks[name](*args, **command)

    def finished(self):
        return self.current_index >= len(self.script)

    def run(self):
        if self.current_index >= len(self.script):
            print("Script complete")
            return False
        output = next(self.current_process)
        if self.current_index < 0:
            output = "Begin!"
        while output != PROCESS_UNFINISHED:
            # add result of last command to namespace (if needed)
            if self.return_name is not None:
                self.namespace[self.return_name] = output
            # new command
            self.current_index += 1
            if self.current_index >= len(self.script):
                return False
            self.execute(self.script[self.current_index])
            output = next(self.current_process)
        return True
