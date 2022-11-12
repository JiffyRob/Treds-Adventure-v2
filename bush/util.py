"""
Bush util

Basic utility module
"""
import pygame

# Constants
QUEUE_EMPTY = "QUEUE_EMPTY"


def rvec(vec: pygame.Vector2):
    """return a list value of a vector, with both coordinates rounded"""
    return [round(vec.x), round(vec.y)]


class IDHandler:
    """
    Simple class for generating and returning numerical ids
    """

    def __init__(self, start: int = 0):
        self._current_id = start - 1

    def get_next(self):
        """Get next ID"""
        self._current_id += 1
        return self._current_id

    def reset(self, start: int):
        """Reset counter back to start"""
        self._current_id = start - 1


class FifoQueue:
    """
    Simple FIFO Queue to cut down on dependencies
    """

    def __init__(self):
        self._list = []

    def add(self, thing):
        self._list.append(thing)

    def pop(self, thing):
        if self._list:
            return self._list.pop(0)
        return QUEUE_EMPTY