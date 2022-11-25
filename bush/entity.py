"""
entity
 - basic entity class
 - entity container group
"""
from typing import Iterable, Sequence, Union

import pygame

from bush import util


class Entity(int):
    """Creates an integer of unique ID"""

    id_handler = util.IDHandler()

    @classmethod
    def reset_ids(cls):
        cls.id_handler.reset()

    def __init__(self):
        super().__init__(id_handler.get_next())
