"""
render
 - rendering components
"""
from typing import Sequence, Union

import pygame

from bush.component import base_component


class RenderGroup(base_component.Component):
    def render(self, surf):
        for components in self.content:
            surf.blit(component.image, component.position)


class CircleRender(base_component.Component):
    def __init__(self, color, radius, entity, position_getter, type):
        self.color = color
        self.radius = radius
        super().__init__(entity, type)

    @property
    def image(self):
        image = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        return image

    @property
    def position(self):
        return self.image.get_rect(center=self.position_getter()).topleft
