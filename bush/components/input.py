"""
input - basic input components
"""
from typing import Callable, Sequence, Union

import pygame

from bush.components import base_component


class DumbButtonInput(base_component.Component):
    """has a series of buttons with callbacks for each.  every frame the button is dow, is calls the callback w/ dt as a param"""

    def __init__(
        self,
        id: Union[int, None] = None,
        entities: Union[Sequence, None] = None,
        key_to_callback_dict: dict[int:Callable] = {},
    ):
        super().__init__(id, entities, "input")
        self._callbacks = key_to_callback_dict

    def set_key(self, key: int, callback: Callable):
        """Add or change a key event to look for."""
        self._callbacks[key] = callback

    def remove_key(self, key: int):
        """Stop checking for a given key"""
        del self._callbacks[key]

    def update(self, dt: float):
        """Check for keys and call callbacks"""
        keys = pygame.key.get_pressed()
        for key in self._callbacks:
            if keys[key]:
                self._callbacks[key](dt)
