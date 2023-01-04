class Command:
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.callback(*self.args, *args, **self.kwargs, **kwargs)

    def done(self):
        return True
