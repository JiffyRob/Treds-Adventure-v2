class StackOverflowError(IndexError):
    pass


class StateStack:
    def __init__(self, max_length=0):
        self.max_length = max_length
        self.stack = []

    def push(self, state):
        if (len(self.stack) < self.max_length) or (not self.max_length):
            state._push(self)
            self.stack.append(state)
        else:
            raise StackOverflowError("Stack max size exceeded.")

    def replace(self, state):
        self.stack[-1] = state

    def pop(self):
        if self.stack:
            self.stack[-1]._remove()
            return self.stack.pop(-1)
        return None

    def clear(self):
        while self.stack:
            self.pop()

    def get_current(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def __repr__(self):
        return f"StateStack {self.stack}"


class StackState:
    def __init__(self, value=None, on_push=lambda: None, on_pop=lambda: None):
        self.value = value
        self._on_push = on_push
        self._on_removal = on_pop
        self._stack = None

    def update(self):
        pass

    def _remove(self):
        self._on_removal()
        self._stack = None

    def pop(self):
        self._stack.pop()

    def _push(self, stack):
        self._on_push()
        self._stack = stack
