import pygame
import pytmx

import player
import static_objects
from bush import animation, asset_handler, entity, level, physics, util

asset_loader = asset_handler.glob_loader
DEFAULT_GROUPS = "main"


def get_anim(x, y, layer_index, tmx_map):
    props = tmx_map.get_tile_properties(x, y, layer_index)
    anim = None
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
        "farmplants_green": pygame.sprite.Group(),
        "farmplants_orange": pygame.sprite.Group(),
        "farmplants": pygame.sprite.Group(),
    }
    instantiators = {
        "player": lambda *args, **kwargs: current_player
        or player.Player(*args, **kwargs),
        "tree": static_objects.Tree,
        "throwable": static_objects.Throwable,
        "farmplant_green": static_objects.green_farmplant,
        "farmplant_orange": static_objects.orange_farmplant,
    }

    for layer_index, layer in enumerate(tmx_map.layers):
        sprite_layer = layer_index
        sprite_layer *= 3  # 3 sub layers in between each map layer (below, main above)
        sprite_layer += 1  # defaults to main layer
        if isinstance(layer, pytmx.TiledTileLayer):
            layer_surface = pygame.Surface(
                (tile_width * map_width, tile_height * map_height), pygame.SRCALPHA
            )
            for x, y, tile in layer.tiles():
                pos = pygame.Vector2(x * tile_width, y * tile_height)
                anim = get_anim(x, y, layer_index, tmx_map)
                layer_surface.blit(tile, pos)
                if anim:
                    tile = level.AnimatedTile(
                        anim,
                        pos + tile_size / 2,
                        layer=sprite_layer + 1,
                    )
                    main_group.add(tile)
            layer_sprite = entity.Entity(
                map_rect.center, layer_surface, layer=sprite_layer
            )
            main_group.add(layer_sprite)
            for group in layer.properties.get("groups", "").split(", "):
                if group not in groups:
                    continue
                layer_sprite = entity.Entity(
                    map_rect.center, layer_surface
                )  # duplicate sprite
                layer_sprite.mask = pygame.mask.from_surface(layer_surface)
                layer_sprite.physics_data = physics.PhysicsData(
                    physics.TYPE_STATIC, groups[group]
                )
                groups[group].add(layer_sprite)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                kwargs = {
                    # y coordinates seem to be one height unit off.  Why?
                    "pos": pygame.Vector2(obj.x, obj.y + obj.height),
                    "id": obj.name or obj.id,
                    "layer": sprite_layer,
                }
                for key, value in groups.items():
                    kwargs[key + "_group"] = value
                if obj.gid:
                    kwargs["image"] = tmx_map.get_tile_image_by_gid(obj.gid)
                sprite = instantiators[obj.type](**kwargs)
                for key in obj.properties.get("groups", DEFAULT_GROUPS).split(", "):
                    if key not in groups:
                        continue
                    groups[key].add(sprite)
    main_group.follow = groups["player"].sprite
    return groups, None
