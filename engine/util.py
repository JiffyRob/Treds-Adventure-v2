"""
Utilities:

Basic functions accessible to all other modules
"""
import pygame


def round_vector(vec):
    return [round(vec.x), round(vec.y)]


class IDHandler:
    """
    Handles incremental integer ID assignment
    """

    def __init__(self, start: int = 0):
        self.current_id = start - 1

    def next(self):
        """Gets next id"""
        self.current_id += 1
        return self.current_id

    def reset(self, start: int = 0):
        """Resets id count to given id if present or 0"""
        self.current_id = start


class CallableNone:
    """An object that can be called or attribute accessed to just return None"""

    def __call__(*args, **kwargs):
        return None

    def __getattribute__(self, other):
        return None

    def __eq__(self, other):
        if other == None:
            return True
        return False
