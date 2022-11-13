"""
render
 - rendering components
"""
from typing import Sequence, Union

import pygame

from bush.component import base_component


class CircleRender(base_component.Component):
    """
    Render a circle as base image.
    has radius and color attributes you can modify
    if outline is true the circle will not be filled in
    """

    def __init__(
        self,
        id: Union[int, None] = None,
        entities: Union[Sequence, None] = None,
        color: Union[pygame.Color, Sequence[int]] = (255, 0, 0),
        radius: int = 16,
        outline: bool = False,
    ):
        super().__init__(id, entities, "render")
        self.color = pygame.Color(*color)
        self.radius = radius
        self.outline = outline

    def render(self, surface, offset: Sequence[float] = (0, 0)):
        """Render my entities's circles to given surface, positions offset by given value"""
        rects = []
        for entity in self.get_entities():
            # if not entity.dirty:
            #    continue
            pos = entity.pos + offset
            rects.append(
                pygame.draw.circle(
                    surface, self.color, pos, self.radius, self.outline
                ).inflate(10, 10)
            )
        return rects
