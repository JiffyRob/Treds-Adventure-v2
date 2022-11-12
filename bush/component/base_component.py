"""
base_component - basic component class
"""
from typing import Sequence, Union

from bush import util


class Component:
    """Base component class.  Don't use this except to subclass your own components

    params:
     - id: int | None = integer id of the component if None will be autoset
     - entities: sequence = list of entities
     - type: str = type of the component, eg "render" or "physics".
                                  Can be your own value, but won't have any special behaviour
    """

    _ids = util.IDHandler()

    @classmethod
    def get_next_id(cls):
        """Return ID of next component to be created.  Increments counter, so use with caution"""
        return cls._ids.get_next()

    @classmethod
    def reset_ids(cls):
        """Reset ID counter to zero"""
        cls._ids.reset(0)

    def __init__(
        self,
        id: Union[int, None] = None,
        entities: Union[Sequence, None] = None,
        type: str = "undef",
    ):
        self._id = id
        self._entities = list(entities)
        self._type = type

    def add_entity(self, entity):
        """Add an entity to this component"""
        self._entities.append(entity)

    def remove_entity(self, entity):
        """
        Remove an entity from this component.

        Returns if entity was part of this component in the first palce
        """
        if entity in self._entities:
            self._entities.remove(entity)
            return True
        return False

    def get_entities(self):
        """Return list of entities that this component contains"""
        return list(self._entities)

    def get_type(self):
        """Return type of the component"""
        return self._type

    def update(self):
        """Call this every frame.  Left empty for now"""
        pass
