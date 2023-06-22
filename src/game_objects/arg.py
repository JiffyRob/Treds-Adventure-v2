from dataclasses import dataclass, field
from typing import Any

import pygame

from bush import animation
from bush.mapping import registry as registry_lib


@dataclass()
class GameObjectArgs:
    pos: pygame.Vector2 = field(
        default_factory=pygame.Vector2
    )  # position of the object
    registry: registry_lib.MapRegistry | None = None  # map registry
    surface: pygame.Surface | animation.Animation | None = (
        None  # visual repr of object (may not be used)
    )
    id: Any = None  # id for object fetching
    layer: int = 4  # layer of the object
    topleft: bool = False  # whether pos is topleft or center.  Positioning done from center normally
    script: str | None = None  # main script (may not be used)
    interaction_script: str | None = None  # script for interaction (may not be used)
    misc: dict | None = None  # misc properties


def from_mapping_object(obj, registry):
    return GameObjectArgs(
        pos=obj.pos,
        registry=registry,
        surface=obj.image,
        id=obj.name,
        layer=obj.layer * 3 + 1,
        topleft=True,
        script=obj.properties.get("script", None),
        interaction_script=obj.properties.get("interaction_script", None),
        misc={"width": obj.width, "height": obj.height, **obj.properties},
    )


def from_projectile_shooter(sprite, direction, surface=None, id=None):
    if surface is None and hasattr(sprite, "projectile_surface"):
        surface = sprite.projectile_surface

    return GameObjectArgs(
        pos=sprite.pos,
        registry=sprite.registry,
        surface=surface,
        id=id,
        layer=sprite.layer,
        misc={
            "fly_direction": direction,
        },
    )
