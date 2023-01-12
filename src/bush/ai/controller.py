from bush import timer
import traceback, sys
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
        self.script = script
        self.state = ExececutionState()
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
                print("waiting...")
                yield PROCESS_UNFINISHED
            print("waiting done!")
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
                lambda value, *args, **kwargs: print(value, *args, **kwargs)
            ),
            "wait": delay,
            **extra_commands,
        }
        print(self.command_callbacks)

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
            print("running", name)
            self.state.current_command = self.command_callbacks[name](*args)
        if isinstance(command, dict):
            name = command.pop("action")
            args = command.pop("args", ())
            self.state.return_name = command.pop(":VAR", None)
            if not self.evaluate(command.pop(":IF", "true")):
                return IF_UNMET
            if return_value:
                print("running with kwwargs", command)
                return next(self.command_callbacks[name](*args, **command))
            self.state.current_command = self.command_callbacks[name](*args, **command)

    def finished(self):
        return self.state.index >= len(self.script)

    def run(self):
        if self.state.index >= len(self.script):
            return False
        output = self.state.get_command_output()
        if self.state.index < 0:
            output = "Begin!"
        print(output)
        while output != PROCESS_UNFINISHED:
            print("next!")
            # add result of last command to namespace (if needed)
            if self.state.return_name is not None:
                self.namespace[self.state.return_name] = output
            # new command
            self.state.index += 1
            if self.state.index >= len(self.script):
                return False
            self.execute(self.script[self.state.index])
            output = self.state.get_command_output()
        return True
