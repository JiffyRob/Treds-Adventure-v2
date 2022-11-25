"""
entity
 - basic entity class
 - entity container group
"""
from typing import Iterable, Sequence, Union

import pygame

from bush import util


class Entity(pygame.sprite.Sprite):
    def __init__(self, rect):
        self.rect = rect.copy()
