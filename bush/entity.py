"""
entity
 - basic entity class
 - entity container group
"""
from typing import Union, Sequence, Iterable

import pygame

from bush import util


class Entity(pygame.sprite.DirtySprite):
    """
    Entity
     - holds an ID, and a list of components
     - can send and receive messages
    """

    _ids = util.IDHandler()

    @classmethod
    def get_next_id(cls):
        """Return ID of next object to be created.  Increments counter, so use with caution"""
        return cls._ids.get_next()

    @classmethod
    def reset_ids(cls):
        """Reset ID counter to zero"""
        cls._ids.reset(0)

    def __init__(
        self, pos: Union[pygame.Vector2, list, tuple] = (0, 0), id=None, *components
    ):
        self.pos = pygame.Vector2(pos)
        self._id = id or self.get_next_id()  # works due to short-ciruit
        super().__init__()
        self._components = list(components)
        self._messages = []

    def get_id(self):
        """Get integer id of the Entity"""
        return self._id

    def rcv_message(self, message):
        """Give a message to this sprite"""
        self._messages.append(message)

    def get_messages(self):
        """Check list of messages"""
        return list(self._messages)


class EntityGroup(pygame.sprite.RenderUpdates):
    """
    A group of Entities

    Can access entities by ID, or receive messages, which are then received by the whole group

    Also has access to individual components
    """

    def __init__(
        self,
        *sprites: Union[pygame.sprite.Sprite, Sequence[pygame.sprite.Sprite]],
    ) -> None:
        self._id_table = {}
        self._components = {}
        super().__init__(*sprites)

    def add(
        self,
        *sprites: Union[
            pygame.sprite.Sprite,
            pygame.sprite.AbstractGroup,
            Iterable[Union[pygame.sprite.Sprite, pygame.sprite.AbstractGroup]],
        ],
    ) -> None:
        """Add entity(s) to the group"""
        # make sure everything is an entity
        entities = [spr for spr in sprites if isinstance(spr, Entity)]
        if len(sprites) != len(entities):
            raise ValueError(f"Sprite list given {sprites} contains non-Entities.")
        # update id and component tables
        for e in entities:
            self._id_table[e.get_id()] = e
            for c in e.get_components():
                if c.get_type() not in self._components.keys():
                    self._components[c.get_type()] = []
                    print("new component type", c.get_type())
                self._components[c.get_type()].append(c)
        return super().add(*sprites)

    def remove(self, *sprites: pygame.sprite.Sprite) -> None:
        """Remove entity(s) from group"""
        # do it for the pygame sprite group (takes care of sprite not in group errors)
        returnval = super().remove(*sprites)
        # update id and component tables
        for sprite in sprites:
            self._id_table.pop(sprite.get_id())
            for c in sprite.get_components():
                self._components[c.get_type()].remove(c)
        return returnval

    def rcv_message(self, message):
        """Get a message and send to all sprites in the group."""
        for sprite in self.sprites():
            sprite.rcv_message(message)

    def get_by_id(self, id: int):
        """Get a sprite via it's id"""
        if id not in self._id_table:
            raise ValueError(f"Given id {id} not found")
        return self._id_table[id]
