"""
Bush!

Component based engine geared toward performance and code simplicity

Named because the leaves of a bush (components of an entity) are defined seperately from the sten (entity)
But mostly because why not.

Copyright 2022 - 2023 John Robinson and Zachary Matzek
Distributed under MIT License
"""
import pygame

pygame.init()

from bush import (
    ai,
    animation,
    asset_handler,
    collision,
    color,
    entity,
    event_binding,
    mapping,
    physics,
    timer,
    util,
    util_load,
)

__all__ = (
    ai,
    animation,
    asset_handler,
    collision,
    color,
    entity,
    event_binding,
    mapping,
    physics,
    timer,
    util,
    util_load,
)
