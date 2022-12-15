class Command:
    def __init__(self):
        pass

    def execute(self, thing, *args, **kwargs):
        pass


class EntityCommand:
    def __init__(self, command_name, *args, **kwargs):
        super().__init__()
        self.command_name = command_name
        self.args = args
        self.kwargs = kwargs

    def execute(self, entity, *args, **kwargs):
        entity.command(self.command_name, *self.args, *args, **self.kwargs, **kwargs)


# Other commands...?
