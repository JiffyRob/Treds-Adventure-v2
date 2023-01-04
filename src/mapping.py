import pygame

import motion_objects
import player
import static_objects
from bush import animation, asset_handler, level

asset_loader = asset_handler.glob_loader
helper_data = asset_loader.load("data/map_objects.json")
object_layers = helper_data["layers"]


def load_map(path, screen_size, current_player=None):
    tmx_map = asset_loader.load(path)
    main_group = level.TopDownGroup(screen_size, screen_size, (0, 0))
    groups = {
        "main": main_group,
        "player": pygame.sprite.GroupSingle(),
    }
    instantiators = {
        "player": lambda *args, **kwargs: current_player
        or player.Player(*args, **kwargs),
    }
    tile_width, tile_height = (16, 16)

    for layer in tmx_map.layers:
        name = layer.name
        if name in {"Ground", "Decor", "Ground Decor", "Collision Decor"}:
            for x, y, tile in layer.tiles():
                pos = pygame.Vector2(x * tile_width, y * tile_height)
                main_group.add(
                    level.AnimatedTile(
                        animation.Animation([tile], 1), pos, object_layers[name]
                    )
                )
        if name in {"Objects", "Flying Objects"}:
            for obj in layer:
                kwargs = {
                    "pos": pygame.Vector2(obj.x, obj.y),
                }
                obj_data = helper_data[obj.template]
                sprite = instantiators[obj_data["type"]](**kwargs)
                for key in obj_data.get("groups", helper_data["default groups"]):
                    print("adding to", key)
                    groups[key].add(sprite)
    return groups
