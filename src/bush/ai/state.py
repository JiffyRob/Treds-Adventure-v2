class StackOverflowError(IndexError):
    pass


class StateStack:
    def __init__(self, max_length=0):
        self.max_length = max_length
        self.stack = []

    def push(self, state):
        if (len(self.stack) < self.max_length) or (not self.max_length):
            self.stack.append(state)
        else:
            raise StackOverflowError("Stack max size exceeded.")

    def replace(self, state):
        self.stack[-1] = state

    def pop(self):
        return self.stack.pop(-1)

    def get_current(self):
        return self.stack[-1]
