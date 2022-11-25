"""
base_component - basic component class
"""
from typing import Sequence, Union

from bush import util


class Component:
    def __init__(self, entity, type):
        self.entity = entity
        self.type = type


class ComponentGroup:
    def __init__(self, *components):
        self.content = list(components)

    def components(self):
        for component in self.content:
            yield component

    def add(self, component):
        self.content.append(component)

    def remove(self, component):
        if component in self.content:
            self.content.remove(component)
