"""
player - class for the player
"""
from typing import Union

import pygame

from bush import components, entity


class Player(entity.Entity):
    """main player of the game

    Args:
        pos: initial position of the player (list, pygame.Vector2, etc.)
        id: player's integer id
    """

    def __init__(self, pos: Union[pygame.Vector2, list, tuple], id=None):
        speed = 96
        input_component = components.DumbButtonInput(
            id=0,
            entities=(self,),
            key_to_callback_dict={
                pygame.K_UP: lambda dt: self.move(
                    pygame.Vector2(0, -speed * dt / 1000)
                ),
                pygame.K_DOWN: lambda dt: self.move(
                    pygame.Vector2(0, speed * dt / 1000)
                ),
                pygame.K_LEFT: lambda dt: self.move(
                    pygame.Vector2(-speed * dt / 1000, 0)
                ),
                pygame.K_RIGHT: lambda dt: self.move(
                    pygame.Vector2(speed * dt / 1000, 0)
                ),
            },
        )
        render_component = components.CircleRender(1, (self,))
        super().__init__(pos, id, input_component, render_component)

    def move(self, vec: pygame.Vector2):
        """Move the player by given vec"""
        self.pos += vec
        self.dirty = 1
