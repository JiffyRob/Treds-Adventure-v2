from collections import namedtuple

GameObjectArgs = namedtuple(
    "GameObjectArgs",
    [
        "pos",
        "registry",
        "surface",
        "id",
        "layer",
        "topleft",
        "script",
        "interaction_script",
        "misc",
    ],
    defaults=[
        (0, 0),  # pos
        None,  # registry
        None,  # surface
        None,  # id
        4,  # layer
        False,  # topleft
        None,  # script             (Enemy and NPC only)
        None,  # interaction_script (NPC Only)
        None,  # misc
    ],
)


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
