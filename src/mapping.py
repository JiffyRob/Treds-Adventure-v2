import os

import pygame
import pytmx

import environment
import static_objects
from bush import animation, asset_handler, entity, level, physics

tiled_loader = asset_handler.AssetHandler(
    os.path.join(asset_handler.glob_loader.base, "tiled")
)


instantiators = {
    "tree": static_objects.Tree,
    "throwable": static_objects.Throwable,
    "farmplant_green": static_objects.green_farmplant,
    "farmplant_orange": static_objects.orange_farmplant,
}

DEFAULT_GROUPS = ("main",)
PLAYER_GROUPS = ("main", "player", "collision", "event")


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


def get_terrain(x, y, layer_index, tmx_map):
    props = tmx_map.get_tile_properties(x, y, layer_index) or {}
    if "terrain" in props:
        return props["terrain"]


def load_map(tmx_map, engine, player_pos):
    if isinstance(tmx_map, str):
        tmx_map = tiled_loader.load(tmx_map)
    event_script = tmx_map.properties.get("script", None)
    if event_script is not None:
        event_script = tiled_loader.load(event_script)
    current_player = engine.player
    screen_size = engine.screen_size
    tile_width, tile_height = tile_size = pygame.Vector2(16, 16)
    map_width, map_height = tmx_map.width, tmx_map.height
    map_rect = pygame.Rect(0, 0, map_width * tile_width, map_height * tile_height)
    main_group = level.TopDownGroup(screen_size, map_rect.size, (0, 0))
    player_layer = 0
    groups = {
        "main": main_group,
        "player": pygame.sprite.GroupSingle(),
        "collision": pygame.sprite.Group(),
        "event": level.EntityGroup(),
        "farmplants_green": pygame.sprite.Group(),
        "farmplants_orange": pygame.sprite.Group(),
        "farmplants": pygame.sprite.Group(),
    }
    map_env = environment.EnvironmentHandler()

    for layer_index, layer in enumerate(tmx_map.layers):
        sprite_layer = (layer_index * 3) + 1
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
                terrain = get_terrain(x, y, layer_index, tmx_map)
                if terrain is not None:
                    print("add terrain", terrain)
                    map_env.add((x, y), terrain)
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
            player_layer = player_layer or layer_index
            for obj in layer:
                kwargs = {
                    # y coordinates seem to be one height unit off.  Why?
                    "pos": pygame.Vector2(obj.x, obj.y + obj.height),
                    "id": obj.name or obj.id,
                    "layer": sprite_layer,
                    "engine": engine,
                    "environment": map_env,
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

    player_layer = tmx_map.properties.get("player_layer", player_layer * 3)
    current_player.kill()
    for key in PLAYER_GROUPS:
        groups[key].add(current_player)
    current_player.change_layer(player_layer)
    current_player.change_collision_group(groups["collision"])
    current_player.change_environment(map_env)
    current_player.rect.center = current_player.pos = pygame.Vector2(player_pos)
    main_group.follow = current_player
    return groups, event_script
