import pygame

import motion_objects
import player
import static_objects
from bush import animation, asset_handler, entity, level, physics, util

asset_loader = asset_handler.glob_loader
helper_data = asset_loader.load("data/map_objects.json")
object_layers = helper_data["layers"]


def get_anim(x, y, tile, layer_index, tmx_map):
    props = tmx_map.get_tile_properties(x, y, layer_index)
    anim = animation.Animation([tile], 1)
    if props is not None and props["frames"]:
        frames = []
        durations = []
        for frame in props["frames"]:
            frames.append(tmx_map.get_tile_image_by_gid(frame.gid))
            durations.append(frame.duration)
        anim = animation.Animation(frames, durations)
    return anim


def load_map(path, screen_size, current_player=None):
    tmx_map = asset_loader.load(path)
    tile_width, tile_height = tile_size = pygame.Vector2(16, 16)
    map_width, map_height = tmx_map.width, tmx_map.height
    map_rect = pygame.Rect(0, 0, map_width * tile_width, map_height * tile_height)
    main_group = level.TopDownGroup(screen_size, map_rect.size, (0, 0))
    groups = {
        "main": main_group,
        "player": pygame.sprite.GroupSingle(),
        "collision": pygame.sprite.Group(),
        "event": level.EntityGroup(),
    }
    instantiators = {
        "player": lambda *args, **kwargs: current_player
        or player.Player(*args, **kwargs),
        "tree": static_objects.Tree,
    }

    for layer_index, layer in enumerate(tmx_map.layers):
        name = layer.name
        if name in {"Ground", "Decor", "Ground Decor"}:
            for x, y, tile in layer.tiles():
                pos = pygame.Vector2(x * tile_width, y * tile_height)
                tile = level.AnimatedTile(
                    get_anim(x, y, tile, layer_index, tmx_map),
                    pos + tile_size / 2,
                    object_layers[name],
                )
                main_group.add(tile)
        if name == "Collision Decor":
            layer_surface = pygame.Surface(
                (tile_width * map_width, tile_height * map_height), pygame.SRCALPHA
            )
            for x, y, tile in layer.tiles():
                pos = pygame.Vector2(x * tile_width, y * tile_height)
                layer_surface.blit(tile, pos)
                tile = level.AnimatedTile(
                    get_anim(x, y, tile, layer_index, tmx_map),
                    pos + tile_size / 2,
                    object_layers[name],
                )
                main_group.add(tile)
            collision_sprite = entity.Entity(map_rect.center, layer_surface)
            collision_sprite.mask = pygame.mask.from_surface(layer_surface)
            collision_sprite.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, groups["collision"]
            )
            groups["collision"].add(collision_sprite)

        if name in {"Objects", "Flying Objects"}:
            for obj in layer:
                kwargs = {
                    "pos": pygame.Vector2(obj.x, obj.y),
                    "collision_group": groups["collision"],
                    "id": obj.id,
                }
                if obj.gid:
                    kwargs["image"] = tmx_map.get_tile_image_by_gid(obj.gid)
                obj_data = helper_data.get(obj.template, None)
                if obj_data is None:
                    continue
                sprite = instantiators[obj_data["type"]](**kwargs)
                for key in obj_data.get("groups", helper_data["default groups"]):
                    groups[key].add(sprite)
    main_group.follow = groups["player"].sprite

    return groups, None
